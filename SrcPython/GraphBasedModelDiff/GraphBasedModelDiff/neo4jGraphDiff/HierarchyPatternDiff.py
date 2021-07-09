from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class HierarchyPatternDiff:

    def __init__(self, connector: Neo4jConnector):
        self.connector: Neo4jConnector = connector

    def diffPatterns(self, entry_init: NodeItem, entry_updated: NodeItem):
        """

        @param entry_init:
        @param entry_updated:
        @return:
        """
        cy_init = Neo4jQueryFactory.get_pattern_by_node_id(entry_init.id)
        cy_updated = Neo4jQueryFactory.get_pattern_by_node_id(entry_updated.id)

        raw_init = self.connector.run_cypher_statement(cy_init)
        raw_updated = self.connector.run_cypher_statement(cy_updated)

        pattern_init: GraphPattern = GraphPattern.from_neo4j_response(raw_init)
        pattern_updated: GraphPattern = GraphPattern.from_neo4j_response(raw_updated)

        # compare patterns and store matched patterns

        return True
