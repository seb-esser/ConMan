from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.neo4jConnector import Neo4jConnector

connector = Neo4jConnector()
connector.connect_driver()

cy = Neo4jQueryFactory.get_distinct_paths_from_node(141)
raw_res = connector.run_cypher_statement(cy)

pattern = GraphPattern.from_neo4j_response(raw_res)

cy = pattern.to_cypher_query()
print(cy)

connector.disconnect_driver()



