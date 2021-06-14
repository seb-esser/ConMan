from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class PatternDetector:

    def __init__(self, connector: Neo4jConnector):
        self.connector: Neo4jConnector = connector

    def search_if_pattern_exists(self, timestamp: str, entry_node_id: int, pattern: GraphPattern) -> bool:
        """
        checks if a specified GraphPattern is in the specified target graph.
        It ignores the p21_id attribute but acknowledges GlobalIds at the moment.
        @param timestamp: timestamp of the target graph
        @param entry_node_id: node id where to start the pattern search
        @param pattern: a GraphPattern object specifying a set of graphEdges
        @return: boolean true-false
        """

        # build cypher statement
        cy = self.search_for_pattern(entry_node_id, pattern)

        # run the cypher statement
        raw = self.connector.run_cypher_statement(cy)

        # encode the result: should be either 0 or 1.
        num_results = len(raw)

        # specify return
        if num_results == 0:
            return False
        elif num_results == 1:
            return True
        else:
            print('Model: {} \t EntryNodeId: {}'.format(timestamp, entry_node_id))
            raise Exception('captured more than 1 pattern. ')

    def search_for_pattern(self, entry_node_id: int, pattern: GraphPattern) -> str:
        """
        creates a cypher query that searches a graph for a specified graph pattern
        @param entry_node_id:
        @param pattern:
        @return:
        """

        # get iterator for all paths inside the given GraphPattern object
        num_paths = pattern.get_number_of_paths()

        # init cypher command
        cy = ""

        # specify entry node in cypher statement
        cy = cy + 'MATCH (en) WHERE ID(en) = {}'.format(entry_node_id)

        # append graph pattern in cypher statement
        # cy = cy + pattern.to_cypher_query()
        cy = cy + pattern.to_cypher_query_indexed()

        # specify return items
        cy = cy + " RETURN ".format(entry_node_id)
        for i in range(num_paths):
            cy = cy + 'path{}, '.format(i)
        # cut off the last ', ' items from cypher string
        cy = cy[:-2]

        return cy


