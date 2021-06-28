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

    def diff_connectionNodes(self):
        """

        @return:
        """

        cy = Neo4jQueryFactory.get_connection_nodes(self.ts_init)
        raw_res = self.connector.run_cypher_statement(cy)
        con_nodes_init: list[NodeItem] = NodeItem.fromNeo4jResponseWouRel(raw_res)

        cy = Neo4jQueryFactory.get_connection_nodes(self.ts_updated)
        raw_res = self.connector.run_cypher_statement(cy)
        con_nodes_updated = NodeItem.fromNeo4jResponseWouRel(raw_res)

        # calc node intersection based on hash and exclude guid as the GUIDs typically change among repeating export
        for n in con_nodes_init:
            cy = Neo4jQueryFactory.get_hash_by_nodeId(label=self.ts_init, nodeId=n.id, attrIgnoreList=['GlobalId', 'p21_id'])
            hash_sum = self.connector.run_cypher_statement(cy, 'hash')[0]
            n.set_hash(hash_sum)

        for n in con_nodes_updated:
            cy = Neo4jQueryFactory.get_hash_by_nodeId(label=self.ts_updated, nodeId=n.id, attrIgnoreList=['GlobalId', 'p21_id'])
            hash_sum = self.connector.run_cypher_statement(cy, 'hash')[0]
            n.set_hash(hash_sum)

        calculator = SetCalculator()
        [nodes_unchanged, nodes_added, nodes_deleted] = calculator.calc_intersection(
            con_nodes_init,
            con_nodes_updated,
            MatchCriteriaEnum.OnHash)

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
