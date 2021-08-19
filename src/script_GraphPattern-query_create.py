from neo4jGraphAnalysis.PatternDetector import PatternDetector
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.neo4jConnector import Neo4jConnector

connector = Neo4jConnector()
connector.connect_driver()

# extract a pattern from a specified graph and start node
ts_init = "ts20210119T085407"
id_init = 4171

cy = Neo4jQueryFactory.get_distinct_paths_from_node(id_init)
raw_res = connector.run_cypher_statement(cy)

# load overall pattern structure from specified graph
pattern = GraphPattern.from_neo4j_response(raw_res)

# load rel attributes (optional step, you can uncomment this method atm)
pattern.load_rel_attrs(connector)

# find pattern in graph with timestamp
ts_updated = 'ts9999'

print('trying to create Graph pattern in target graph with timestamp label > {} < '.format(ts_updated))
cy = pattern.to_cypher_create(timestamp=ts_updated)
print(cy)
connector.run_cypher_statement(cy)

connector.disconnect_driver()



