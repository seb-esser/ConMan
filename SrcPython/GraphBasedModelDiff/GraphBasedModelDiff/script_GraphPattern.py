from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.neo4jConnector import Neo4jConnector

connector = Neo4jConnector()
connector.connect_driver()

cy = Neo4jQueryFactory.get_pattern_by_node_id(141)
raw_res = connector.run_cypher_statement(cy, 'pattern')

pattern = GraphPattern.from_neo4j_response(raw_res)

connector.disconnect_driver()



