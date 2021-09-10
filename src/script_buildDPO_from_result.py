import jsonpickle

from neo4jGraphDiff.GraphDelta import GraphDelta

with open('result_initts20121017T152740-updtts20121017T154702.json') as f:
    content = f.read()

print("[INFO] loading result json....")
result: GraphDelta = jsonpickle.decode(content)
print("[INFO] DONE. ")

# ToDo: these lists should be included in the result object. Apparently, these changes are not yet captured.
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
label_init = "ts20121017T152740"
label_updt = "ts20121017T154702"


connector = Neo4jConnector()
connector.connect_driver()


def calcDPO(obj_guid: str, label: str):
    """

    """
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
    nodes_outs = NodeItem.fromNeo4jResponse(raw_outs)
    nodes_ins = NodeItem.fromNeo4jResponse(raw_outs)  # die können eigentlich gar nicht existieren, weil sie sonst einer anderen struktur zugeordnet wären.
    print('\t Num nodes to be removed: {}'.format(len(removedPattern.get_unified_node_set())))
    print('\t Num nodes embedding SecondaryReferences: ')
    for n in nodes_outs:
        primNode: NodeItem = result.node_matching_table.get_parent_primaryNode(n)
        cy = "MATCH pa = shortestpath((pn:{0} {{GlobalId: \"{1}\" }})-[*..10]->(e)) WHERE ID(e) = {2} return pa," \
             " NODES(pa), RELATIONSHIPS(pa)".format(label, primNode.attrs["GlobalId"], n.id)
        raw = connector.run_cypher_statement(cy)
        patt = GraphPattern.from_neo4j_response(raw)
        print('\t\t refNode ID: {:>6} parent: {:>6} path length: {}'.format(n.id, primNode.id,
                                                                            len(patt.get_unified_node_set())))
        # print(cy)
    cy = "MATCH embeddingPrimary = (n:PrimaryNode:{0} {{GlobalId: \"{1}\"}})<--(c:ConnectionNode)-->(prim:PrimaryNode) " \
         "RETURN embeddingPrimary, NODES(embeddingPrimary), RELATIONSHIPS(embeddingPrimary)".format(label, obj_guid)
    # print(cy)
    raw = connector.run_cypher_statement(cy)
    primary_embedding_pattern = GraphPattern.from_neo4j_response(raw)
    primary_embedding_pattern.load_rel_attrs(connector=connector)
    print('\t Num nodes embedding primary structure (including ConnectionNodes): {}'
          .format(len(primary_embedding_pattern.get_unified_node_set())))
    print('\n')


print('REMOVED components:')
for guid in guids_removed:
    calcDPO(guid, label_init)

print('')
print('INSERTED components:')
for guid in guids_added:
    calcDPO(guid, label_updt)

connector.disconnect_driver()



