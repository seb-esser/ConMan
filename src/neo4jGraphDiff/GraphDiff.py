from neo4jGraphDiff.AbsGraphDiff import AbsGraphDiff
from neo4jGraphDiff.Caption.NodeMatchingTable import NodePair
from neo4jGraphDiff.Caption.StructureModification import StructureModification
from neo4jGraphDiff.Config.Configuration import Configuration
from neo4jGraphDiff.Config.ConfiguratorEnums import MatchCriteriaEnum
from neo4jGraphDiff.GraphDelta import GraphDelta
from neo4jGraphDiff.ResourceDiff import ResourceDiff
from neo4jGraphDiff.SetCalculator import SetCalculator
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem
from neo4j_middleware.neo4jConnector import Neo4jConnector


class GraphDiff(AbsGraphDiff):

    def __init__(self, connector: Neo4jConnector, ts_init: str, ts_updated: str):
        super().__init__(label_init=ts_init, label_updated=ts_updated, connector=connector,
                         configuration=Configuration.basic_config())

        # calc diff on resource structure
        self.resource_diff = ResourceDiff(connector=self.connector,
                                          label_init=self.label_init,
                                          label_updated=self.label_updated,
                                          config=self.configuration)

    def diff_subgraphs(self, entry_init: NodeItem, entry_updated: NodeItem):
        """
        RENAME TO calculate_graph_delta()
        performs a hierarchy-driven substructure traversal. GraphDelta is available under self.delta
        @param entry_init:
        @param entry_updated:
        @return:
        """
        # recursion over hierarchical breakdown
        self.__move_level_down(entry_init, entry_updated)

        # compare connection nodes
        self.__compare_connection_nodes()

        #  --- post processing ---
        prim_nodes_init = [x.init_node for x in
                           self.resource_diff.result.node_matching_table.get_all_primaryNode_pairs()]
        prim_nodes_updt = [x.updated_node for x in
                           self.resource_diff.result.node_matching_table.get_all_primaryNode_pairs()]

        for n in prim_nodes_init:
            if n.id == -1:
                prim_nodes_init.remove(n)
        for n in prim_nodes_updt:
            if n.id == -1:
                prim_nodes_updt.remove(n)

        set_calculator = SetCalculator()
        [unc, added, deleted] = set_calculator.calc_intersection(
            set_A=prim_nodes_init,
            set_B=prim_nodes_updt,
            intersection_method=MatchCriteriaEnum.OnGuid)

        # log unchanged nodes
        for n1, n2 in unc:
            self.resource_diff.result.node_matching_table.add_matched_nodes(n1, n2)

        # log added and deleted nodes on primary structure
        for ad in added:
            self.resource_diff.result.node_matching_table.add_matched_nodes(NodeItem(node_id=-1), ad)
            self.resource_diff.result.capture_structure_mod(entry_init, ad, 'added')
        for de in deleted:
            self.resource_diff.result.node_matching_table.add_matched_nodes(de, NodeItem(node_id=-1))
            self.resource_diff.result.capture_structure_mod(entry_init, de, 'deleted')
        # -- compare edgeSet --

        # load edge data
        # edges_init = self.__load_edges(self.label_init)
        # edges_updt = self.__load_edges(self.label_updated)
        #
        # edge_matching = EdgeMatchingTable()
        # edge_matching.calculate(edges_init, edges_updt)

        # returns the delta calculated during the diff process
        return self.resource_diff.get_delta()

    def __move_level_down(self, entry_init: NodeItem, entry_updated: NodeItem):
        """
        RENAME TO move_hierarchy_level_down()
        @param entry_init:
        @param entry_updated:
        @return:
        """
        self.resource_diff.result.node_matching_table.add_matched_nodes(entry_init, entry_updated)

        print('[DIFF] Running subgraph Diff under PrimaryNodes {} and {}'.format(entry_init.id, entry_updated.id))
        # run diff and get node matching
        self.resource_diff.diff_subgraphs(entry_init, entry_updated)

        # run subgraph diff again and consider already matched node pairs now
        # query next primary nodes
        cy_next_nodes_init = Neo4jQueryFactory.get_hierarchical_prim_nodes(
            node_id=entry_init.id,
            exclude_nodes=self.resource_diff.result.node_matching_table.get_all_primaryNode_pairs())
        cy_next_nodes_upd = Neo4jQueryFactory.get_hierarchical_prim_nodes(
            node_id=entry_updated.id,
            exclude_nodes=self.resource_diff.result.node_matching_table.get_all_primaryNode_pairs())

        raw_init = self.connector.run_cypher_statement(cy_next_nodes_init)
        raw_updated = self.connector.run_cypher_statement(cy_next_nodes_upd)

        next_nodes_init = NodeItem.from_neo4j_response(raw_init)
        next_nodes_upd = NodeItem.from_neo4j_response(raw_updated)

        # check if no new children got found:
        if len(next_nodes_init) == 0 and len(next_nodes_upd) == 0:
            return

        # remove nodes from node set that have been already detected as removed or inserted
        rmv_lst_init = []
        rmv_lst_updt = []

        for n in next_nodes_init:
            if n in self.resource_diff.result.get_node_list_removed():
                rmv_lst_init.append(n)
        for n in next_nodes_upd:
            if n in self.resource_diff.result.get_node_list_inserted():
                rmv_lst_updt.append(n)

        next_nodes_init = [x for x in next_nodes_init if x not in rmv_lst_init]
        next_nodes_upd = [x for x in next_nodes_upd if x not in rmv_lst_updt]

        # ToDo: refactor and clean up code here

        # calc node intersection
        set_calculator = SetCalculator()
        [unc, added, deleted] = set_calculator.calc_intersection(
            next_nodes_init, next_nodes_upd, MatchCriteriaEnum.OnGuid)

        # log added and deleted nodes on primary structure
        for ad in added:
            self.resource_diff.result.structure_updates.append(
                StructureModification(parent=entry_updated, child=ad, modification_type="added"))
            self.resource_diff.result.node_matching_table.add_matched_nodes(NodeItem(node_id=-1), ad)

        for de in deleted:
            self.resource_diff.result.structure_updates.append(
                StructureModification(parent=entry_init, child=de, modification_type="deleted"))
            self.resource_diff.result.node_matching_table.add_matched_nodes(de, NodeItem(node_id=-1))

        # kick recursion for next hierarchy level if pair was not already visited
        for pair in unc:
            if NodePair(pair[0],
                        pair[1]) not in self.resource_diff.result.node_matching_table.get_all_primaryNode_pairs():
                self.__move_level_down(pair[0], pair[1])
                # ToDo: here is the entry point for each primary node which is necessary for pMods

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

    def get_result(self) -> GraphDelta:
        res: GraphDelta = self.resource_diff.get_delta()
        return res

    def get_result_json(self):
        import jsonpickle
        print('saving delta ... ')
        f = open('GraphDelta_init{}-updt{}.json'.format(self.label_init, self.label_updated), 'w')
        f.write(jsonpickle.dumps(self.resource_diff.get_delta()))
        f.close()
        print('saving delta: DONE. ')

    def build_equivalent_to_edges(self):
        delta = self.get_result()
        for p in delta.node_matching_table.matched_nodes:
            # print(p)
            cy = """
                MATCH (n) WHERE ID(n)={0}
                MATCH (m) WHERE ID(m)= {1}
                MERGE (n)-[:EQUIVALENT_TO]->(m)
                """.format(p.init_node.id, p.updated_node.id)
            self.connector.run_cypher_statement(cy)

    def __compare_connection_nodes(self):
        ts_init = self.label_init
        ts_updated = self.label_updated

        cy = """
        match patternInit = (prim1init:PrimaryNode:{0})<-[:rel]-(cinit:ConnectionNode:{0})-[:rel]->(prim2init:PrimaryNode:{0})
        match patternUpdt = (prim1updt:PrimaryNode:{1})<-[:rel]-(cupdt:ConnectionNode:{1})-[:rel]->(prim2updt:PrimaryNode:{1}) 
        WHERE prim1init.GlobalId = prim1updt.GlobalId AND prim2init.GlobalId = prim2updt.GlobalId AND cinit.EntityType = cupdt.EntityType
        RETURN DISTINCT cinit as n1, cupdt as n2
        """.format(ts_init, ts_updated)

        pairs_raw = self.connector.run_cypher_statement(cy)
        for p in pairs_raw:
            node_init, node_updt = NodeItem.from_neo4j_response(p)
            self.resource_diff.result.node_matching_table.add_matched_nodes(node_init, node_updt)

