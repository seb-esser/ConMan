""" packages """
from typing import List

from neo4jGraphDiff.Caption.NodeMatchingTable import NodeMatchingTable, NodePair
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern

""" modules """
from neo4jGraphDiff.Config.ConfiguratorEnums import MatchCriteriaEnum
from neo4jGraphDiff.Caption.SubstructureDiffResult import SubstructureDiffResult
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeDiffData import NodeDiffData
from neo4j_middleware.ResponseParser.NodeItem import NodeItem

from neo4jGraphDiff.AbsDirectedSubgraphDiff import AbsDirectedSubgraphDiff
from neo4j_middleware.ResponseParser.GraphPath import GraphPath


class DfsIsomorphismCalculator(AbsDirectedSubgraphDiff):
    """ compares two directed subgraphs based on a node diff of nodes and recursively analyses the entire subgraph """

    def __init__(self, connector, label_init, label_updated, config):
        super().__init__(connector, label_init, label_updated, config)
        self.matchingTable: NodeMatchingTable = NodeMatchingTable()
        self.diffContainer = SubstructureDiffResult(method="Node-Diff")

    def get_diff_result(self):
        return self.diffContainer

    # public overwrite method requested by abstract superclass AbsDirectedSubgraphDiff
    def diff_subgraphs(self, node_init: NodeItem, node_updated: NodeItem, matched_nodes = None):

        # clear sub result container
        self.diffContainer = SubstructureDiffResult(method="Node-Diff")

        # store entry points
        self.diffContainer.set_nodes(node_init, node_updated)

        if matched_nodes is not None:
            self.matchingTable.matched_nodes += matched_nodes

        # start recursion
        self.__compare_children(node_init, node_updated, indent=0)

        return self.diffContainer

    async def diff_subgraphs_async(self, node_init: NodeItem, node_updated: NodeItem):
        """

        """
        self.diffContainer.set_nodes(node_init, node_updated)

        # start recursion
        self.__compare_children(node_init, node_updated)

    def __compare_children(self, node_init, node_updated, indent = 0):
        """
        queries the all child nodes of a node and compares the results between
        the initial and the updated graph based on AttrDiff
        """

        desiredMatchMethod = self.configuration.DiffSettings.MatchingType_Childs

        self.diffContainer.increaseRecursionCounter()

        if self.toConsole():
            print("".ljust(indent * 4) +
                  'Check children of NodeId {} and NodeId {}'.format(node_init.id, node_updated.id))

        # get children nodes
        children_init = self.get_children_nodes(self.label_init, node_init.id)
        children_updated = self.get_children_nodes(self.label_updated, node_updated.id)

        # apply DiffIgnore -> Ignore nodes if requested
        children_init = self.apply_DiffIgnore_Nodes(children_init)
        children_updated = self.apply_DiffIgnore_Nodes(children_updated)

        # leave node?
        if len(children_init) == 0 and len(children_updated) == 0:
            if self.toConsole():
                print("".ljust(indent * 4) + ' leaf node.')
            return

        # calc hashes if necessary for matching method
        if desiredMatchMethod == MatchCriteriaEnum.OnHash:
            # calc hashes for init and updated
            children_init = self.__get_hashes_of_nodes(self.label_init, children_init, indent)
            children_updated = self.__get_hashes_of_nodes(self.label_updated, children_updated, indent)

        # compare children and raise an dissimilarity if necessary.
        [nodes_unchanged, nodes_added, nodes_deleted] = self.utils.calc_intersection(children_init, children_updated,
                                                                                     desiredMatchMethod)

        # check if nodes in nodes_unchanged got already matched but a previous subtree analysis
        import copy
        intmed_unc = copy.deepcopy(nodes_unchanged)
        for pair in intmed_unc:
            if NodePair(pair[0], pair[1]) in self.matchingTable.matched_nodes:
                # stop recursion
                continue
            elif self.matchingTable.node_involved_in_nodePair(pair[0]):
                # init node of matched pair was already involved in a matching
                nodes_unchanged.remove(pair)
            elif self.matchingTable.node_involved_in_nodePair(pair[1]):
                # updated node of matched pair was already involved in a matching
                nodes_unchanged.remove(pair)


        if self.toConsole():
            print('')
            print("".ljust(indent * 4) + 'children unchanged: {}'.format(nodes_unchanged))
            print("".ljust(indent * 4) + 'children added: {}'.format(nodes_added))
            print("".ljust(indent * 4) + 'children deleted: {} \n'.format(nodes_deleted))

        if len(nodes_added) != 0 or len(nodes_deleted) != 0:
            # log structural modifications
            for ch in nodes_added:
                self.diffContainer.logStructureModification(node_updated.id, ch.id, 'added')

            for ch in nodes_deleted:
                self.diffContainer.logStructureModification(node_init.id, ch.id, 'deleted')

        # --- 3 --- loop over all matching child pairs and detect their similarities and differences

        # check the nodes that have the same relationship OR the same EntityType and the same node type: 
        for matchingChildPair in nodes_unchanged:
            # detect changes on property level between both matching nodes
            self.__calcPropertyDifference(matchingChildPair[0], matchingChildPair[1])

            for n1, n2 in nodes_unchanged:
                if self.diffContainer.nodeMatchingTable.node_pair_in_matching_table(NodePair(n1, n2)):
                    # logged this pair already, continue for loop
                    continue
                else:
                    self.diffContainer.nodeMatchingTable.add_matched_nodes(n1, n2)

            # run recursion for children if "NoChange" or "Modified" happened
            self.__compare_children(matchingChildPair[0],
                                    matchingChildPair[1],
                                    indent=indent + 1)

        return

    def __apply_diffIgnore(self, diff, IgnoreAttrs: List[str]):
        """

        @param diff:
        @param IgnoreAttrs:
        @return:
        """
        for ignore in IgnoreAttrs:
            if ignore in diff.AttrsUnchanged:       del diff.AttrsUnchanged[ignore]
            if ignore in diff.AttrsAdded:           del diff.AttrsAdded[ignore]
            if ignore in diff.AttrsDeleted:         del diff.AttrsDeleted[ignore]
            if ignore in diff.AttrsModified:        del diff.AttrsModified[ignore]

        return diff

    def __calcPropertyDifference(self, node_init: NodeItem,
                                 node_updated: NodeItem):
        """
        calculates if a semantic modification was applied on two nodes
        @param node_init:
        @param node_updated:
        @return:
        """
        # compare two nodes
        cypher = Neo4jQueryFactory.diff_nodes(node_init.id, node_updated.id)
        raw = self.connector.run_cypher_statement(cypher)

        nodeDifference = NodeDiffData.fromNeo4jResponse(raw)

        # apply DiffIgnore on diff result
        ignoreAttrs = self.configuration.DiffSettings.diffIgnoreAttrs
        nodeDiff = self.__apply_diffIgnore(nodeDifference, ignoreAttrs)

        if self.toConsole():
            print('comparing node {} to node {} after applying DiffIgnore:'.format(node_init.id, node_updated.id))

        # case 1: no modifications on pair
        if nodeDiff.nodesAreSimilar():
            # nodes are similar
            if self.toConsole():
                print('[RESULT]: child nodes match')

        else:
            self.diffContainer.isSimilar = False
            # log modifications
            root_init = self.diffContainer.RootNode_init
            root_updated = self.diffContainer.RootNode_updated

            pattern = self.__get_pattern(root_init.id, node_init.id)

            pmod_list = nodeDiff.createPModDefinitions(node_init.id, node_updated.id, pattern=pattern)
            # append modifications to container
            self.diffContainer.propertyModifications.extend(pmod_list)

    def __get_hashes_of_nodes(self, label: str, nodeList: List[NodeItem], indent = 0) -> List[NodeItem]:
        """
        calculates the hash_value sum for each node in a given node list
        @param label: the model identifier
        @param nodeList: a list of nodes the hash value should be calculated
        @param indent: printing stuff (might be removed soon)
        @return:
        """

        ignore_attrs = self.configuration.DiffSettings.diffIgnoreAttrs  # list of strings
        # calc corresponding hash_value
        for node in nodeList:
            # calc hash_value of current node
            cypher_hash = Neo4jQueryFactory.get_hash_by_nodeId(label, node.id, ignore_attrs)
            hash_value = self.connector.run_cypher_statement(cypher_hash)[0][0]

            node.set_hash(hash_value)

        if self.toConsole():
            print("".ljust(indent * 4) + 'Calculated hashes for model >> {} <<:'.format(label))
            for node in nodeList:
                print("".ljust(indent * 4) + '\t NodeID: {:<4} \t hash_value: {}'.format(node.id, node.hash_value))

        return nodeList

    def __get_pattern(self, root_node_id: int, current_node_id: int) -> GraphPattern:
        """

        @param root_node_id:
        @param current_node_id:
        @return:
        """
        cy = Neo4jQueryFactory.get_directed_path_by_nodeId(node_id_start=root_node_id, node_id_target=current_node_id)
        res = self.connector.run_cypher_statement(cy)

        path = GraphPath.from_neo4j_response(res)
        pattern = GraphPattern(paths=[path])
        return pattern
