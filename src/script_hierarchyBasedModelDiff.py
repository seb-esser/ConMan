from neo4jGraphDiff.HierarchyPatternDiff import HierarchyPatternDiff
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector

connector = Neo4jConnector()

connector.connect_driver()

# placement example
# ts_init = 'ts20210623T091748'
# ts_updated = 'ts20210623T091749'

# Solibri example
ts_init = 'ts20121017T152740'
ts_updated = 'ts20121017T154702'

print("Do you really want to re-run the diff calculation? ")
confirm = input("[y, n]")

if confirm != "y":
    exit()

connector.run_cypher_statement("Match(n:{})-[r:SIMILAR_TO]-(m:{}) DELETE r".format(ts_init, ts_updated))

# get topmost entry nodes
raw_init = connector.run_cypher_statement(
    """
    MATCH (n:PrimaryNode:{})
    WHERE n.EntityType = "IfcProject"
    RETURN ID(n), n.EntityType, PROPERTIES(n), LABELS(n)
    """.format(ts_init))
raw_updated = connector.run_cypher_statement(
    """
    MATCH (n:PrimaryNode:{})
    WHERE n.EntityType = "IfcProject"
    RETURN ID(n), n.EntityType, PROPERTIES(n), LABELS(n)
    """.format(ts_updated))

entry_init: NodeItem = NodeItem.fromNeo4jResponseWouRel(raw_init)[0]
entry_updated: NodeItem = NodeItem.fromNeo4jResponseWouRel(raw_updated)[0]

pDiff = HierarchyPatternDiff(connector=connector, ts_init=ts_init, ts_updated=ts_updated)
result = pDiff.diff_subgraphs(entry_init, entry_updated)
print(result)

# Create SIMILAR_TO relationships to mark all nodePairs that are matched
for p in result.node_matching_table.matched_nodes:
    # print(p)
    cy = """
    MATCH (n) WHERE ID(n)={0}
    MATCH (m) WHERE ID(m)= {1}
    MERGE (n)-[:SIMILAR_TO]->(m)
    """.format(p.init_node.id, p.updated_node.id)
    connector.run_cypher_statement(cy)

# Find all nodes that do not have a SIMILAR_TO relationship
cy = Neo4jQueryFactory.get_all_nodes_wou_SIMILARTO_rel(ts_updated)
print(cy)
raw_res = connector.run_cypher_statement(cy)
nodes = NodeItem.fromNeo4jResponseWouRel(raw_res)

