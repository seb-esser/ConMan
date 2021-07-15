from neo4jGraphDiff.Config.Configuration import Configuration
from neo4jGraphDiff.HierarchyPatternDiff import HierarchyPatternDiff
from neo4jGraphDiff.SecondaryNodeDiff import DfsIsomorphismCalculator
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector

connector = Neo4jConnector()

connector.connect_driver()

ts_init = 'ts20210623T091748'
ts_updated = 'ts20210623T091749'

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

for p in result.nodeMatchingTable.matched_nodes:
    print(p)

connector.disconnect_driver()

