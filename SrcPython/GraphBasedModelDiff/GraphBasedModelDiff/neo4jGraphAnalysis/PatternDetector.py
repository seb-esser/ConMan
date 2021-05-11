from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class PatternDetector:

    def __init__(self, connector: Neo4jConnector):
        self.connector: Neo4jConnector = connector

    def search_if_pattern_exists(self, timestamp: str, pattern: GraphPattern) -> bool:

        # find entry node
        entry_node_id: int = 141
        cy = Neo4jQueryFactory.get_node_data_by_id(entry_node_id)
        raw = self.connector.run_cypher_statement(cy)
        entry_node: NodeItem = NodeItem.fromNeo4jResponse(raw)[0]



        # next:
        # if node_exists: True and pattern_exists: False: run DFS
        # if node_exists: False:

        return True

