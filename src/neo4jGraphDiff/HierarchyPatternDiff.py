from typing import List

from neo4jGraphDiff.AbsDirectedSubgraphDiff import AbsDirectedSubgraphDiff
from neo4jGraphDiff.Caption.NodeMatchingTable import NodePair
from neo4jGraphDiff.Caption.StructureModification import StructureModification
from neo4jGraphDiff.Config.Configuration import Configuration
from neo4jGraphDiff.Config.ConfiguratorEnums import MatchCriteriaEnum
from neo4jGraphDiff.Result import Result
from neo4jGraphDiff.SecondaryNodeDiff import DfsIsomorphismCalculator
from neo4jGraphDiff.SetCalculator import SetCalculator
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
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

        # capture result
        self.result = Result(label_init=self.label_init, label_updated=self.label_updated)

        # this list is used to track already visited primary nodes!
        self.visited_primary_nodes: List[NodePair] = []

    def diff_subgraphs(self, entry_init: NodeItem, entry_updated: NodeItem):
        """
        performs a hierarchy-driven substructure traversal. Result is available under self.result
        @param entry_init:
        @param entry_updated:
        @return:
        """
        # recursion
        self.__move_level_down(entry_init, entry_updated)

        #  --- post processing ---
        prim_nodes_init = [x.init_node for x in self.result.node_matching_table.get_all_primaryNode_pairs()]
        prim_nodes_updt = [x.updated_node for x in self.result.node_matching_table.get_all_primaryNode_pairs()]

        con_init = NodeItem.fromNeo4jResponseWouRel(
            self.connector.run_cypher_statement(
                Neo4jQueryFactory.get_connection_nodes(self.label_init)
            ))

        con_updt = NodeItem.fromNeo4jResponseWouRel(
            self.connector.run_cypher_statement(
                Neo4jQueryFactory.get_connection_nodes(self.label_updated)
            ))

        for n in prim_nodes_init:
            if n.id == -1:
                prim_nodes_init.remove(n)
        for n in prim_nodes_updt:
            if n.id == -1:
                prim_nodes_updt.remove(n)

        set_calculator = SetCalculator()
        [unc, added, deleted] = set_calculator.calc_intersection(
            set_A=prim_nodes_init + con_init,
            set_B=prim_nodes_updt + con_updt,
            intersection_method=MatchCriteriaEnum.OnGuid)

        # log unchanged nodes
        for n1, n2 in unc:
            self.result.node_matching_table.add_matched_nodes(n1, n2)

        # log added and deleted nodes on primary structure
        for ad in added:
            self.diff_engine.diffContainer.logStructureModification(entry_updated, ad, 'added')
            self.visited_primary_nodes.append(NodePair(NodeItem(nodeId=-1), ad))
        for de in deleted:
            self.diff_engine.diffContainer.logStructureModification(entry_init, de, 'deleted')
            self.visited_primary_nodes.append(NodePair(de, NodeItem(nodeId=-1)))

        # -- compare edgeSet --

        # load edge data
        # edges_init = self.__load_edges(self.label_init)
        # edges_updt = self.__load_edges(self.label_updated)
        #
        # edge_matching = EdgeMatchingTable()
        # edge_matching.calculate(edges_init, edges_updt)

        return self.result

    def __move_level_down(self, entry_init: NodeItem, entry_updated: NodeItem):
        """

        @param entry_init:
        @param entry_updated:
        @return:
        """
        self.result.node_matching_table.add_matched_nodes(entry_init, entry_updated)

        print('[DIFF] Running subgraph Diff under PrimaryNodes {} and {}'.format(entry_init.id, entry_updated.id))
        # run diff and get node matching
        sub_result = self.diff_engine.diff_subgraphs(entry_init, entry_updated, self.result.node_matching_table)

        # integrate sub_result in main result including smod, pmod and NodeMatchingTable
        self.result.append_sub_result(sub_res=sub_result)

        # run subgraph diff again and consider already matched node pairs now
        # query next primary nodes
        cy_next_nodes_init = Neo4jQueryFactory.get_hierarchical_prim_nodes(
            node_id=entry_init.id,
            exclude_nodes=self.result.node_matching_table.get_all_primaryNode_pairs())
        cy_next_nodes_upd = Neo4jQueryFactory.get_hierarchical_prim_nodes(
            node_id=entry_updated.id,
            exclude_nodes=self.result.node_matching_table.get_all_primaryNode_pairs())

        raw_init = self.connector.run_cypher_statement(cy_next_nodes_init)
        raw_updated = self.connector.run_cypher_statement(cy_next_nodes_upd)

        next_nodes_init = NodeItem.fromNeo4jResponseWouRel(raw_init)
        next_nodes_upd = NodeItem.fromNeo4jResponseWouRel(raw_updated)

        # check if no new children got found:
        if len(next_nodes_init) == 0 and len(next_nodes_upd) == 0:
            return self.diff_engine.diffContainer

        # remove nodes from node set that have been already detected as removed or inserted
        rmv_lst_init =[]
        rmv_lst_updt =[]

        for n in next_nodes_init:
            if n in self.result.get_node_list_removed():
                rmv_lst_init.append(n)
        for n in next_nodes_upd:
            if n in self.result.get_node_list_inserted():
                rmv_lst_updt.append(n)

        next_nodes_init = [x for x in next_nodes_init if x not in rmv_lst_init]
        next_nodes_upd = [x for x in next_nodes_upd if x not in rmv_lst_updt]

        #ToDo: refactor and clean up code here

        # calc node intersection
        set_calculator = SetCalculator()
        [unc, added, deleted] = set_calculator.calc_intersection(
            next_nodes_init, next_nodes_upd, MatchCriteriaEnum.OnGuid)

        # log added and deleted nodes on primary structure
        for ad in added:
            self.result.structure_updates.append(StructureModification(parent=entry_updated, child=ad, modificationType="added"))
            self.visited_primary_nodes.append(NodePair(NodeItem(nodeId=-1), ad))
        for de in deleted:
            self.result.structure_updates.append(StructureModification(parent=entry_init, child=de, modificationType="deleted"))
            self.visited_primary_nodes.append(NodePair(de, NodeItem(nodeId=-1)))

        # kick recursion for next hierarchy level if pair was not already visited
        for pair in unc:
            if NodePair(pair[0], pair[1]) not in self.result.node_matching_table.get_all_primaryNode_pairs():
                self.__move_level_down(pair[0], pair[1])

    def __load_edges(self, label):
        """
        loads all edges from a graph specified by its label
        @param label:
        @return:
        """
        cy = Neo4jQueryFactory.get_all_relationships(label)
        raw = self.connector.run_cypher_statement(cy)
        pattern = GraphPattern.from_neo4j_response(raw)
        paths = pattern.get_unified_edge_set()

        edges = []
        for path in paths:
            # extract edge from pattern
            edge = path.segments[0]

            # load relationship attributes
            cy = Neo4jQueryFactory.get_relationship_attributes(rel_id=edge.edge_id)
            raw = self.connector.run_cypher_statement(cy)[0]
            edge.set_attributes(raw)
            edges.append(edge)

        return edges
