from neo4jGraphDiff.Config.ConfiguratorEnums import MatchCriteriaEnum
from neo4jGraphDiff.SetCalculator import SetCalculator
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class ConnectionNodeDiff:

    def __init__(self, connector: Neo4jConnector, label_init: str, label_updated: str):
        """

        @type connector: object
        @param label_init:
        @param label_updated:
        """
        self.connector = connector
        self.ts_init = label_init
        self.ts_updated = label_updated

    def diff_connection_nodes(self):
        """

        @return:
        """

        cy = Neo4jQueryFactory.get_connection_nodes(self.ts_init)
        raw_res = self.connector.run_cypher_statement(cy)
        con_nodes_init = NodeItem.fromNeo4jResponseWouRel(raw_res)

        cy = Neo4jQueryFactory.get_connection_nodes(self.ts_updated)
        raw_res = self.connector.run_cypher_statement(cy)
        con_nodes_updated = NodeItem.fromNeo4jResponseWouRel(raw_res)

        calculator = SetCalculator()
        [nodes_unchanged, nodes_added, nodes_deleted] = calculator.calc_intersection(
            con_nodes_init,
            con_nodes_updated,
            MatchCriteriaEnum.OnGuid)

        patterns_init = []
        for node in con_nodes_init:
            # get all connection node patterns
            cy = Neo4jQueryFactory.get_conNodes_patterns(node.id)
            raw_res = self.connector.run_cypher_statement(cy)
            pattern = GraphPattern.from_neo4j_response(raw_res)
            pattern.load_rel_attrs(self.connector)
            patterns_init.append(pattern)

        patterns_updated = []
        for node in con_nodes_updated:
            # get all connection node patterns
            cy = Neo4jQueryFactory.get_conNodes_patterns(node.id)
            raw_res = self.connector.run_cypher_statement(cy)
            pattern = GraphPattern.from_neo4j_response(raw_res)
            pattern.load_rel_attrs(self.connector)
            patterns_updated.append(pattern)

        # calc pattern intersection
        print(patterns_updated)

        return [nodes_unchanged, nodes_added, nodes_deleted]
