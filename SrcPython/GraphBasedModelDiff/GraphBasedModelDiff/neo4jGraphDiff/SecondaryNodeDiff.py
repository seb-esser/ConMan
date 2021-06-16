""" packages """
from typing import List

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
        return super().__init__(connector, label_init, label_updated, config)

    # public overwrite method requested by abstract superclass AbsDirectedSubgraphDiff
    def diff_subgraphs(self, node_init: NodeItem, node_updated: NodeItem) -> SubstructureDiffResult:

        diffContainer = SubstructureDiffResult(method="Node-Diff", root_init=node_init, root_updated=node_updated)

        # start recursion
        diffContainer = self.__compare_children(node_init, node_updated, diffContainer, indent=0)
        return diffContainer

    async def diff_subgraphs_async(self, node_init: NodeItem, node_updated: NodeItem) -> SubstructureDiffResult:
        """

        """
        diffContainer = SubstructureDiffResult(method="Node-Diff", root_init=node_init, root_updated=node_updated)

        # start recursion
        diffContainer = self.__compare_children(node_init, node_updated, diffContainer)

        return diffContainer

    def __compare_children(self, node_init, node_updated, diff_result_container, indent = 0):
        """
        queries the all child nodes of a node and compares the results between
        the initial and the updated graph based on AttrDiff
        """

        desiredMatchMethod = self.configuration.DiffSettings.MatchingType_Childs

        diff_result_container.increaseRecursionCounter()

        if self.toConsole():
            print("".ljust(indent * 4) +
                  'Check children of NodeId {} and NodeId {}'.format(node_init.id, node_updated.id))

        # get children nodes
        children_init = self.get_children_nodes(self.label_init, node_init.id)
        children_updated = self.get_children_nodes(self.label_updated, node_updated.id)

        # leave node?
        if len(children_init) == 0 and len(children_updated) == 0:
            if self.toConsole():
                print("".ljust(indent * 4) + ' leaf node.')
            return diff_result_container

        # calc hashes if necessary for matching method
        if desiredMatchMethod == MatchCriteriaEnum.OnHash:
            # calc hashes for init and updated
            children_init = self.__get_hashes_of_nodes(self.label_init, children_init, indent)
            children_updated = self.__get_hashes_of_nodes(self.label_updated, children_updated, indent)

        # apply DiffIgnore -> Ignore nodes if requested        
        children_init = self.apply_DiffIgnore_Nodes(children_init)
        children_updated = self.apply_DiffIgnore_Nodes(children_updated)

        # compare children and raise an dissimilarity if necessary.
        [nodes_unchanged, nodes_added, nodes_deleted] = self.utils.calc_intersection(children_init, children_updated,
                                                                                     desiredMatchMethod)

        if self.toConsole():
            print('')
            print("".ljust(indent * 4) + 'children unchanged: {}'.format(nodes_unchanged))
            print("".ljust(indent * 4) + 'children added: {}'.format(nodes_added))
            print("".ljust(indent * 4) + 'children deleted: {} \n'.format(nodes_deleted))

        if len(nodes_added) != 0 or len(nodes_deleted) != 0:
            # log structural modifications
            for ch in nodes_added:
                diff_result_container.logStructureModification(node_updated.id, ch.id, 'added')

            for ch in nodes_deleted:
                diff_result_container.logStructureModification(node_init.id, ch.id, 'deleted')

        # --- 3 --- loop over all matching child pairs and detect their similarities and differences

        # check the nodes that have the same relationship OR the same EntityType and the same node type: 
        for matchingChildPair in nodes_unchanged:
            # detect changes on property level between both matching nodes
            diff_result_container = self.__calcPropertyDifference(
                diff_result_container, matchingChildPair[0], matchingChildPair[1])

            # run recursion for children if "NoChange" or "Modified" happened
            diff_result_container = self.__compare_children(matchingChildPair[0],
                                                            matchingChildPair[1],
                                                            diff_result_container,
                                                            indent=indent + 1)

        return diff_result_container

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

    def __calcPropertyDifference(self, diff_result_container: SubstructureDiffResult, node_init: NodeItem,
                                 node_updated: NodeItem) -> SubstructureDiffResult:
        """
        calculates if a semantic modification was applied on two nodes
        @param diff_result_container: reporter instance
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
            diff_result_container.isSimilar = False
            # log modifications
            root_init = diff_result_container.RootNode_init
            root_updated = diff_result_container.RootNode_updated

            path_init = self.__get_path(root_init.id, node_init.id)
            path_updated = self.__get_path(root_updated.id, node_updated.id)

            pmod_list = nodeDiff.createPModDefinitions(node_init.id, node_updated.id, path_init=path_init,
                                                       path_updated=path_updated)
            # append modifications to container
            diff_result_container.propertyModifications.extend(pmod_list)
        return diff_result_container

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

    def __get_path(self, root_node_id: int, current_node_id: int) -> GraphPath:
        """

        @param root_node_id:
        @param current_node_id:
        @return:
        """
        cy = Neo4jQueryFactory.get_directed_path_by_nodeId(node_id_start=root_node_id, node_id_target=current_node_id)
        res = self.connector.run_cypher_statement(cy)

        path = GraphPath.from_neo4j_response(res)
        return path
