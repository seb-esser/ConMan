from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class PatternDetector:

    def __init__(self, connector: Neo4jConnector):
        self.connector: Neo4jConnector = connector

    def search_if_pattern_exists(self, timestamp: str, entry_node_id: int, pattern: GraphPattern) -> bool:
        cy = ""

        cy = cy + 'MATCH (en) WHERE ID(en) = {}'.format(entry_node_id)
        cy = cy + pattern.to_cypher_query()
        cy = cy + "RETURN en".format(entry_node_id)
        raw = self.connector.run_cypher_statement(cy)
        num_results = len(raw)

        if num_results == 0:
            return False
        elif num_results == 1:
            return True
        else:
            print('Model: {} \t EntryNodeId: {}'.format(timestamp, entry_node_id))
            raise Exception('captured more than 1 pattern. ')


