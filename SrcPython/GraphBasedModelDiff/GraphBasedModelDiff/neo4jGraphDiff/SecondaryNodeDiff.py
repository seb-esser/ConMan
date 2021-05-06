""" packages """
from neo4j_middleware.ResponseParser.GraphPath import GraphPath

""" modules """
from neo4jGraphDiff.Config.ConfiguratorEnums import MatchCriteriaEnum
from neo4jGraphDiff.Caption.SubstructureDiffResult import SubstructureDiffResult
from neo4j_middleware.Neo4jQueryFactory import Neo4jQueryFactory
from neo4j_middleware.ResponseParser.NodeDiffData import NodeDiffData
from neo4j_middleware.ResponseParser.NodeItem import NodeItem

from neo4jGraphDiff.AbsDirectedSubgraphDiff import AbsDirectedSubgraphDiff


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

    def __compare_children(self, node_init, node_updated, diff_result_container, indent=0):
        """
        queries the all child nodes of a node and compares the results between
        the initial and the updated graph based on AttrDiff
        """

        desiredMatchMethod = self.configuration.DiffSettings.MatchingType_Childs

        diff_result_container.increaseRecursionCounter()

        if self.toConsole():
            print("".ljust(indent * 4) + 'Check children of NodeId {} and NodeId {}'.format(node_init.id,
                                                                                            node_updated.id))

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
            childs_init = self.__get_hashes_of_nodes(self.label_init, children_init, indent)
            childs_updated = self.__get_hashes_of_nodes(self.label_updated, children_updated, indent)

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
            diff_result_container = self.__calcPropertyDifference(diff_result_container, node_init, node_updated)

            # run recursion for children if "NoChange" or "Modified" happened
            diff_result_container = self.__compare_children(matchingChildPair[0],
                                                            matchingChildPair[1],
                                                            diff_result_container,
                                                            indent=indent + 1)

            # end for loop 

        return diff_result_container

    def __apply_diffIgnore(self, diff, IgnoreAttrs):
        """ removes the attributes stated in the used DiffIgnore file from the diff result of apoc """
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
        if nodeDiff.nodesAreSimilar() == True:
            # nodes are similar
            if self.toConsole():
                print('[RESULT]: child nodes match')

        # case 2: modified attrs on pair but no added/deleted attrs
        elif nodeDiff.nodesHaveUpdatedAttributeValues() == True:

            # log modification
            for modifiedAttr in nodeDiff.AttrsModified.items():
                if self.toConsole():
                    print(modifiedAttr)

                # ToDo: move extraction of data from tuple to higher representation
                attr_name = modifiedAttr[0]
                val_old = modifiedAttr[1]['left']
                val_new = modifiedAttr[1]['right']

                # calculate graph path to node
                primary_init = diff_result_container.RootNode_init.id
                primary_updated = diff_result_container.RootNode_updated.id

                cy = Neo4jQueryFactory.get_directed_path_by_nodeId(primary_init, node_init.id)
                path_init_raw = self.connector.run_cypher_statement(cy)

                cy = Neo4jQueryFactory.get_directed_path_by_nodeId(primary_updated, node_updated.id)
                path_updated_raw = self.connector.run_cypher_statement(cy)

                path_init = GraphPath.from_neo4j_response(path_init_raw)
                path_updated = GraphPath.from_neo4j_response(path_updated_raw)

                diff_result_container.logNodeModification(node_init.id, node_updated.id, attr_name, 'modified', val_old,
                                                          val_new, path_init, path_updated)

        # case 3: added/deleted attrs. Break recursion
        else:
            if self.toConsole():
                print('[RESULT]: detected unsimilarity between nodes {} and {}'.format(node_init.id, node_updated.id))
                print(nodeDiff)

            # -- log result --

            # calculate graph path to node
            primary_init = diff_result_container.RootNode_init.id
            primary_updated = diff_result_container.RootNode_updated.id

            cy = Neo4jQueryFactory.get_directed_path_by_nodeId(primary_init, node_init.id)
            path_init_raw = self.connector.run_cypher_statement(cy)

            cy = Neo4jQueryFactory.get_directed_path_by_nodeId(primary_updated, node_updated.id)
            path_updated_raw = self.connector.run_cypher_statement(cy)

            path_init = GraphPath.from_neo4j_response(path_init_raw)
            path_updated = GraphPath.from_neo4j_response(path_updated_raw)

            # log modified
            for modAttr in nodeDiff.AttrsModified.items():
                attr_name = modAttr[0]
                val_old = modAttr[1]['left']
                val_new = modAttr[1]['right']

                diff_result_container.logNodeModification(node_init.id, node_updated.id, attr_name, 'modified', val_old,
                                                          val_new, path_init, path_updated)

            # log added
            for addedAttr in nodeDiff.AttrsAdded.items():
                attr_name = addedAttr[0]
                val_new = addedAttr[1]
                diff_result_container.logNodeModification(None, node_updated.id, attr_name, 'added', None, val_new, path_init, path_updated)

            # log deleted
            for delAttr in nodeDiff.AttrsDeleted.items():
                attr_name = delAttr[0]
                val_new = delAttr[1]
                diff_result_container.logNodeModification(node_init.id, None, attr_name, 'deleted', val_old, None, path_init, path_updated)

        return diff_result_container

    def __get_hashes_of_nodes(self, label: str, nodeList: list, indent=0) -> list:
        """
        calculates the hash_value sum for each node in a given node list
        @param label: the model identifier
        @param nodeList:
        @param indent:
        @return:
        """

        ignore_attrs = self.configuration.DiffSettings.diffIgnoreAttrs  # list of strings
        # calc corresponding hash_value
        for node in nodeList:
            child_node_id = node.id
            relType = node.relType
            # calc hash_value of current node
            cypher_hash = Neo4jQueryFactory.get_hash_by_nodeId(label, child_node_id, ignore_attrs)
            hash = self.connector.run_cypher_statement(cypher_hash)[0][0]

            node.set_hash(hash)

        if self.toConsole():
            print("".ljust(indent * 4) + 'Calculated hashes for model >> {} <<:'.format(label))
            for node in nodeList:
                print("".ljust(indent * 4) + '\t NodeID: {:<4} \t hash_value: {}'.format(node.id, node.hash_value))

        return nodeList
