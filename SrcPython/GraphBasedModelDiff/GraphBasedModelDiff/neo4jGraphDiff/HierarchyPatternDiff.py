from typing import List

from neo4jGraphDiff.AbsDirectedSubgraphDiff import AbsDirectedSubgraphDiff
from neo4jGraphDiff.Caption.NodeMatchingTable import NodePair
from neo4jGraphDiff.Caption.SubstructureDiffResult import SubstructureDiffResult
from neo4jGraphDiff.Config.Configuration import Configuration
from neo4jGraphDiff.Config.ConfiguratorEnums import MatchCriteriaEnum
from neo4jGraphDiff.SecondaryNodeDiff import DfsIsomorphismCalculator
from neo4jGraphDiff.SetCalculator import SetCalculator
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class HierarchyPatternDiff(AbsDirectedSubgraphDiff):

    def __init__(self, connector: Neo4jConnector, ts_init: str, ts_updated: str):
        super().__init__(label_init=ts_init, label_updated=ts_updated, connector=connector,
                         configuration=Configuration.basic_config())

        # calc diff on substructure
        self.diff_engine = DfsIsomorphismCalculator(connector=self.connector,
                                               label_init=self.label_init,
                                               label_updated=self.label_updated,
                                               config=self.configuration)

        # this list is used to track already visited primary nodes!
        self.visited_primary_nodes: List[NodePair] = []

    def diff_subgraphs(self, entry_init: NodeItem, entry_updated: NodeItem):
        """

        @param entry_init:
        @param entry_updated:
        @return:
        """

        self.visited_primary_nodes.append(NodePair(entry_init, entry_updated))
        self.diff_engine.diffContainer.nodeMatchingTable.add_matched_nodes(entry_init, entry_updated)

        # run diff and get node matching
        self.diff_engine.diff_subgraphs(entry_init, entry_updated)

        # run subgraph diff again and consider already matched node pairs now
        cy_next_nodes_init = Neo4jQueryFactory.get_hierarchical_prim_nodes(node_id=entry_init.id,
                                                                           exclude_nodes=self.visited_primary_nodes)
        cy_next_nodes_upd = Neo4jQueryFactory.get_hierarchical_prim_nodes(node_id=entry_updated.id,
                                                                          exclude_nodes=self.visited_primary_nodes)

        raw_init = self.connector.run_cypher_statement(cy_next_nodes_init)
        raw_updated = self.connector.run_cypher_statement(cy_next_nodes_upd)

        next_nodes_init = NodeItem.fromNeo4jResponseWouRel(raw_init)
        next_nodes_upd = NodeItem.fromNeo4jResponseWouRel(raw_updated)

        # check if no new children got found:
        if len(next_nodes_init) == 0 and len(next_nodes_upd) == 0:
            return self.diff_engine.diffContainer

        # calc node intersection
        set_calculator = SetCalculator()
        [unc, added, deleted] = set_calculator.calc_intersection(
            next_nodes_init, next_nodes_upd, MatchCriteriaEnum.OnGuid)

        # log added and deleted nodes on primary structure
        for ad in added:
            self.diff_engine.diffContainer.logStructureModification(entry_updated.id, ad.id, 'added')
            self.visited_primary_nodes.append(NodePair(NodeItem(nodeId=-1), ad))
        for de in deleted:
            self.diff_engine.diffContainer.logStructureModification(entry_init.id, de.id, 'deleted')
            self.visited_primary_nodes.append(NodePair(de, NodeItem(nodeId=-1)))

        # kick recursion for next hierarchy level
        for pair in unc:
            self.diff_subgraphs(pair[0], pair[1])

        return self.diff_engine.diffContainer

