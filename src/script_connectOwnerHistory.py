from neo4jGraphDiff.Caption.NodeMatchingTable import NodePair
from neo4jGraphDiff.Config.Configuration import Configuration
from neo4jGraphDiff.SecondaryNodeDiff import DfsIsomorphismCalculator
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector

label_init = "ts20121017T152740"
label_updt = "ts20121017T154702"

connector = Neo4jConnector()
connector.connect_driver()

oh_init = connector.run_cypher_statement("MATCH (n:{0} {{EntityType: \"IfcOwnerHistory\" }})"
                                         " RETURN ID(n), n.EntityType, PROPERTIES(n), LABELS(n)".format(label_init))
oh_updt = connector.run_cypher_statement("MATCH (n:{0} {{EntityType: \"IfcOwnerHistory\" }}) "
                                         "RETURN ID(n), n.EntityType, PROPERTIES(n), LABELS(n)".format(label_updt))

init = NodeItem.fromNeo4jResponseWouRel(oh_init)[0]
updt = NodeItem.fromNeo4jResponseWouRel(oh_updt)[0]

calculator = DfsIsomorphismCalculator(connector, label_init, label_updt, config=Configuration.basic_config())
res = calculator.diff_subgraphs(node_init=init, node_updated=updt)

res.nodeMatchingTable.matched_nodes.append(NodePair(init, updt))

for p in res.nodeMatchingTable.matched_nodes:
    # print(p)
    cy = """
    MATCH (n) WHERE ID(n)={0}
    MATCH (m) WHERE ID(m)= {1}
    MERGE (n)-[:SIMILAR_TO]->(m)
    """.format(p.init_node.id, p.updated_node.id)
    connector.run_cypher_statement(cy)

connector.disconnect_driver()

