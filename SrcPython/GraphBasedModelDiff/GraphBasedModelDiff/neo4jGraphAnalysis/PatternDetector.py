from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class PatternDetector:

    def __init__(self, connector: Neo4jConnector):
        self.connector: Neo4jConnector = connector

    def search_if_pattern_exists(self, timestamp: str, entry_node_id: int, pattern: GraphPattern) -> bool:
        cy = ""

        cy = cy + 'MATCH (en) '
        cy = cy + pattern.to_cypher_query()
        cy = cy + "RETURN en".format(entry_node_id)
        raw = self.connector.run_cypher_statement(cy)
        print(raw)


        # next:
        # if node_exists: True and pattern_exists: False: run DFS
        # if node_exists: False:

        return True

