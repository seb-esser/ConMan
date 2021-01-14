
    
import abc

from .DirectedSubgraphDiff import DirectedSubgraphDiff
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory

from neo4jGraphDiff.DiffResult import DiffResult 

class HashDiff(DirectedSubgraphDiff):
    """description of class"""

    def __init__(self, connector, label_init, label_updated, diffIgnorePath=None, LogtoConsole = False , considerRelType = False):
        self.considerRelType = considerRelType
        return super().__init__(connector, label_init, label_updated, diffIgnorePath=diffIgnorePath, toConsole=LogtoConsole)
    
    def diffSubgraphs(self, node_init, node_updated): 

        # ToDo: return diff results and not only True/False in case of a spotted difference between init and updated
        diffContainer = DiffResult(method = "Hash-Diff")
                
        # start recursion
        diffContainer = self.__compareChildren(node_init, node_updated, diffContainer)
        return diffContainer



    def __compareChildren(self, node_init, node_updated, diff_container, indent = 0, considerRelType = False):
        """  queries the all child nodes of a node and compares the results between the initial and the updated graph based on hash comparison """

        if self.toConsole:
            print("".ljust(indent*4) + 'Check children of NodeId {} and NodeId {}'.format(node_init.id, node_updated.id))

        # get children data
        children_init =     self._DirectedSubgraphDiff__getChildren(self.label_init, node_init.id, indent +1)
        children_updated =  self._DirectedSubgraphDiff__getChildren(self.label_updated, node_updated.id, indent +1)

        # leave node
        if len(children_init) == 0 and len(children_updated) == 0: 
            if self.toConsole:
                print("".ljust(indent*4) + ' leaf node.')
            return diff_container

        # calc hashes for init and updated
        childs_init = self.__getHashesOfNodes(self.label_init, children_init, indent)
        childs_updated = self.__getHashesOfNodes(self.label_updated, children_updated, indent)

        # apply DiffIgnore -> Ingore nodes if requested
        if self.UseDiffIgnore:
            children_init = self._DirectedSubgraphDiff__applyDiffIgnore_Nodes(children_init)
            children_updated = self._DirectedSubgraphDiff__applyDiffIgnore_Nodes(children_updated)


        # compare children and raise an unsimilarity if necessary.
        [nodes_unchanged, nodes_added, nodes_deleted] = self.utils.CompareNodesByHash(childs_init, childs_updated, self.considerRelType)

        if self.toConsole:
            print('')
            print("".ljust(indent*4) + 'children unchanged: {}'.format(nodes_unchanged))
            print("".ljust(indent*4) + 'children added: {}'.format(nodes_added))
            print("".ljust(indent*4) + 'children deleted: {} \n'.format(nodes_deleted))

        if (len(nodes_added) != 0 or len(nodes_deleted) != 0):
            diff_container.isSimilar = False
            # log unsimilarities
            for addedNode in nodes_added:
                diff_container.logStructureModification(node_init.id, addedNode.id, "added")
            for deletedNode in nodes_deleted:
                diff_container.logStructureModification(node_updated.id, deletedNode.id, "deleted")

            return diff_container

        # loop over all (similar) children
        for similarChild in nodes_unchanged:
            # ToDo: log unchanged nodes if requested

            # trigger recursion
            diff_container = self.__compareChildren(similarChild[0], similarChild[1], diff_container, indent + 1)
            if diff_container.isSimilar == False:
                return diff_container

        return diff_container


    def __getHashesOfNodes(self, label, nodeList, indent = 0):
        return_val = []

        ignore_attrs = self.utils.diffIngore.ignore_attrs

        # calc corresponding hash
        for node in nodeList: 
            child_node_id = node.id
            relType = node.relType
            # calc hash of current node
            cypher_hash = neo4jQueryFactory.GetHashByNodeId(label, child_node_id, ignore_attrs )
            hash = self.connector.run_cypher_statement(cypher_hash)[0][0]

            node.setHash(hash)

        if self.toConsole: 
            print("".ljust(indent*4) + 'Calculated hashes for model >> {} <<:'.format(label))
            for node in nodeList:
                print("".ljust(indent*4) + '\t NodeID: {:<4} \t hash: {}'.format(node.id, node.hash))


        return nodeList
