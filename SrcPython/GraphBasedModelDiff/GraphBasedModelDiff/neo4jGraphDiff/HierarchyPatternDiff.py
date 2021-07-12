from neo4jGraphDiff.Config.Configuration import Configuration
from neo4jGraphDiff.SecondaryNodeDiff import DfsIsomorphismCalculator
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class HierarchyPatternDiff:

    def __init__(self, connector: Neo4jConnector, ts_init: str, ts_updated: str):
        self.connector: Neo4jConnector = connector
        self.label_init: str = ts_init
        self.label_updated: str = ts_updated

    def diffPatterns(self, entry_init: NodeItem, entry_updated: NodeItem):
        """

        @param entry_init:
        @param entry_updated:
        @return:
        """
        cy_init = Neo4jQueryFactory.get_node_by_id(entry_init.id)
        cy_updated = Neo4jQueryFactory.get_node_by_id(entry_updated.id)

        raw_init = self.connector.run_cypher_statement(cy_init)
        raw_updated = self.connector.run_cypher_statement(cy_updated)

        entry_init = NodeItem.fromNeo4jResponseWouRel(raw_init)[0]
        entry_updated = NodeItem.fromNeo4jResponseWouRel(raw_updated)[0]

        substruc_diff = DfsIsomorphismCalculator(connector=self.connector,
                                                 label_init=self.label_init,
                                                 label_updated=self.label_updated,
                                                 config=Configuration.basic_config())

        diff_res = substruc_diff.diff_subgraphs(entry_init.id, entry_updated.id)


        return True
