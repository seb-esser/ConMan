import jsonpickle
from re import search

from neo4jGraphDiff.GraphDelta import GraphDelta

with open('GraphDelta_initts20121017T152740-updtts20121017T154702.json') as f:
    content = f.read()

print("[INFO] loading delta json....")
result: GraphDelta = jsonpickle.decode(content)
print("[INFO] DONE. ")

# ToDo: these lists should be included in the delta object. Apparently, these changes are not yet captured.
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector

guids_removed = [
    "32xlMB3wy8fOpMzyHpakTe",
    "2SeQTQUdv7Su2MXgROLa2$",
    "3cAF6Z6l1AaAN$n1Dh1jf8"
]

guids_added = [
    "1VQM4R42pgD4M9fKP5xbei",
    "1xYoyrIGL3SwPhpyfPm_Nq",
    "0I_5eIRzL7QhiRmNZWVpkh",
    "1VaaDkOIb9kR_m_Kk3toPA",
    "2D5DFc$nD1Xub_Y4N75Yhn"
]
label_init = result.ts_init
label_updt = result.ts_updated


connector = Neo4jConnector()
connector.connect_driver()


def remove_trim_errors(result: GraphDelta):
    """
    removes false errors caused by the Model->Graph parser
    @param result:
    @return:
    """
    counter = 0
    pmods_to_be_removed = []

    for pm in result.property_updates:
        if search("Trim", pm.attrName):
            pmods_to_be_removed.append(pm)
            counter += 1

    print('removed Trim errors: {}'.format(counter))
    result.property_updates = [x for x in result.property_updates if x not in pmods_to_be_removed]


def calcDPO(obj_guid: str, label: str):
    """

    """

    node_counter = 0

    print("\tComponent: {}".format(obj_guid))
    # -- 1 -- query nodes to be removed (as a graph pattern)
    cy = """
    MATCH pa = (n:PrimaryNode:{0} {{GlobalId: \"{1}\"}})-[*..10]->(sec:SecondaryNode:{0})
    WHERE NOT (sec)-[:SIMILAR_TO]->()
    RETURN pa, NODES(pa), RELATIONSHIPS(pa)
    """.format(label, obj_guid)
    raw = connector.run_cypher_statement(cy)
    removedPattern = GraphPattern.from_neo4j_response(raw)
    removedPattern.get_unified_edge_set()
    removedPattern.load_rel_attrs(connector=connector)
    # print(cy + '\n --- --- \n')
    # -- 2 -- calculate embedding of removed component
    cy_ptrs = """
    MATCH removeNodes = (n:PrimaryNode:{0} {{GlobalId: \"{1}\"}})-[:rel*..10]->(sec:SecondaryNode:{0})
    WHERE NOT (sec)-[:SIMILAR_TO]-() 
    OPTIONAL MATCH inclinedPointers = (sec)<-[:rel]-(extPtr_in)-[:SIMILAR_TO]-(a)
    OPTIONAL MATCH outgoingPointers = (sec)-[:rel]->(extPtr_out)-[:SIMILAR_TO]-(b)

    WITH COLLECT(extPtr_out) as outs, COLLECT(extPtr_in) as ins
    RETURN [val in outs WHERE val is not null] as ptrs_out, [val in ins WHERE val is not null] as ptrs_in
    """.format(label, obj_guid)
    raw_outs, raw_ins = connector.run_cypher_statement(cy_ptrs)[0]
    nodes_outs = NodeItem.from_neo4j_response(raw_outs)
    nodes_ins = NodeItem.from_neo4j_response(raw_outs)

    node_counter += len(removedPattern.get_unified_node_set())

    print('\t Num nodes to be removed: {}'.format(len(removedPattern.get_unified_node_set())))
    print('\t Num nodes embedding SecondaryReferences: ')
    # print('\t   OUT: ')
    for n in nodes_outs:
        primNode: NodeItem = result.node_matching_table.get_parent_primaryNode(n)
        cy = "MATCH pa = shortestpath((pn:{0} {{GlobalId: \"{1}\" }})-[*..10]->(e)) WHERE ID(e) = {2} return pa," \
             " NODES(pa), RELATIONSHIPS(pa)".format(label, primNode.attrs["GlobalId"], n.id)
        raw = connector.run_cypher_statement(cy)
        patt = GraphPattern.from_neo4j_response(raw)
        print('\t\t refNode ID: {:>6} parent: {:>6} path length: {}'.format(n.id, primNode.id,
                                                                            len(patt.get_unified_node_set())))
        node_counter += len(patt.get_unified_node_set())

    # print('\t   IN: ')
    # for n in nodes_ins:
    #     primNode: NodeItem = result.node_matching_table.get_parent_primaryNode(n)
    #     cy = "MATCH pa = shortestpath((pn:{0} {{GlobalId: \"{1}\" }})-[*..10]->(e)) WHERE ID(e) = {2} return pa," \
    #          " NODES(pa), RELATIONSHIPS(pa)".format(label, primNode.attrs["GlobalId"], n.id)
    #     raw = connector.run_cypher_statement(cy)
    #     patt = GraphPattern.from_neo4j_response(raw)
    #     print('\t\t refNode ID: {:>6} parent: {:>6} path length: {}'.format(n.id, primNode.id,
    #                                                                         len(patt.get_unified_node_set())))

    cy = "MATCH embeddingPrimary = (n:PrimaryNode:{0} {{GlobalId: \"{1}\"}})<--(c:ConnectionNode)-->(prim:PrimaryNode) " \
         "RETURN embeddingPrimary, NODES(embeddingPrimary), RELATIONSHIPS(embeddingPrimary)".format(label, obj_guid)
    # print(cy)
    raw = connector.run_cypher_statement(cy)
    primary_embedding_pattern = GraphPattern.from_neo4j_response(raw)
    primary_embedding_pattern.load_rel_attrs(connector=connector)
    print('\t Num nodes embedding primary structure (including ConnectionNodes): {}'
          .format(len(primary_embedding_pattern.get_unified_node_set())))

    node_counter += len(primary_embedding_pattern.get_unified_node_set())
    print('\n')
    return node_counter


print('Run pre-processing and remove all detected pMods with "Trim" attributes. \n')
remove_trim_errors(result=result)
project_renaming = result.property_updates[1]
result.property_updates.remove(project_renaming)
result.sort_pMods_by_guid()
# result.property_updates.append(project_renaming)
print('Preprocessing DONE. \n')

guids = []
path_lengths = []

for pm in result.property_updates:
    entity = pm.pattern.get_entry_node().attrs['EntityType']
    guid = pm.pattern.get_entry_node().attrs['GlobalId']
    if guid not in guids:
         guids.append(guid)

    path_lengths.append(len(pm.pattern.paths[0].segments))

    print("{:>12}\t{:<20}\t{:<25}\t{:<100}\t{:<100}".format(guid, entity, pm.attrName, pm.valueOld, pm.valueNew))

print('\nTotal number of modified components: {}'.format(len(guids)))
print('Number of modified attributes: {} \n'.format(len(result.property_updates)))

print('Average path length: {}'.format(sum(path_lengths)/len(path_lengths)))
print('Min path length: {}'.format(min(path_lengths)))
print('Max path length: {} \n'.format(max(path_lengths)))


print('REMOVED components:')
for guid in guids_removed:
    num_nodes = calcDPO(guid, label_init)

print('')
print('INSERTED components:')
for guid in guids_added:
    calcDPO(guid, label_updt)

connector.disconnect_driver()



