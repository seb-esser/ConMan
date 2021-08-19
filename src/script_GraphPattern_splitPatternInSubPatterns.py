from neo4jGraphAnalysis.PatternDetector import PatternDetector
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector

connector = Neo4jConnector()
connector.connect_driver()

# extract a pattern from a specified graph and start node
ts_init = "ts20210616T145520"
id_init = 37

cy = Neo4jQueryFactory.get_distinct_paths_from_node(id_init)
raw_res = connector.run_cypher_statement(cy)

# load overall pattern structure from specified graph
pattern = GraphPattern.from_neo4j_response(raw_res)

# load rel attributes (optional step, you can uncomment this method atm)
pattern.load_rel_attrs(connector)

# load entry node of pattern
cy = Neo4jQueryFactory.get_node(id_init)
raw_res = connector.run_cypher_statement(cy, 'n')
node = NodeItem.fromNeo4jResponse(raw_res)[0]

sub_patterns = pattern.split_pattern()

connector.disconnect_driver()



