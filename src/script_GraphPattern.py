from neo4jGraphAnalysis.PatternDetector import PatternDetector
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
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

# find pattern in graph with timestamp
ts_updated = 'ts20210616T145520'
id_updated = 37

detector = PatternDetector(connector=connector)
exists = detector.search_if_pattern_exists(ts_updated, id_updated, pattern)

print('Staged pattern derived from node {0} in > {1} < exists'
      ' under node {2} in {3}: {4}'.format(id_init, ts_init, id_updated, ts_updated, exists))

connector.disconnect_driver()



