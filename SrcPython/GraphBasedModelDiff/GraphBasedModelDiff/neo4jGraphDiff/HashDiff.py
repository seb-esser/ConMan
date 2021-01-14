
    
import abc

from .DirectedSubgraphDiff import DirectedSubgraphDiff
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory

from neo4jGraphDiff.DiffResult import DiffResult 

class HashDiff(DirectedSubgraphDiff):
    """description of class"""

    def __init__(self, connector, label_init, label_updated, diffIgnorePath=None, LogtoConsole = False , considerRelType = False):
        self.considerRelType = considerRelType
        return super().__init__(connector, label_init, label_updated, diffIgnorePath=diffIgnorePath, toConsole=LogtoConsole)
    
    def diffSubgraphs(self, nodeId_init, nodeId_updated): 

        # ToDo: return diff results and not only True/False in case of a spotted difference between init and updated
        diffContainer = DiffResult(method = "Hash-Diff")
        diffContainer = self.__compareChildren(nodeId_init, nodeId_updated, diffContainer)
        return diffContainer

    # compare children method. recursive usage

    def __compareChildren(self, nodeId_init, nodeId_updated, diffContainer, indent = 0, considerRelType = False ): 
        """  queries the all child nodes of a node and compares the results between the initial and the updated graph based on hash comparison """

        if self.toConsole:
            print("".ljust(indent*4) + 'Check children of NodeId {} and NodeId {}'.format(nodeId_init, nodeId_updated))

        # get children data
        children_init =     self._DirectedSubgraphDiff__getChildren(self.label_init, nodeId_init, indent +1)
        children_updated =  self._DirectedSubgraphDiff__getChildren(self.label_updated, nodeId_updated, indent +1)

        # leave node
        if len(children_init) == 0 and len(children_updated) == 0: 
            if self.toConsole:
                print("".ljust(indent*4) + ' leaf node.')
            return diffContainer

        # calc hashes for init and updated
        childs_init = self.__getHashesOfNodes(self.label_init, children_init, indent)
        childs_updated = self.__getHashesOfNodes(self.label_updated, children_updated, indent)

        # apply DiffIgnore -> Ingore nodes if requested
        if self.UseDiffIgnore: 
            children_init = self._DirectedSubgraphDiff__applyDiffIgnore_Nodes(children_init)
            children_updated = self._DirectedSubgraphDiff__applyDiffIgnore_Nodes(children_updated)


        # compare children and raise an unsimilarity if necessary.
        similarity = self.utils.CompareNodesByHash(childs_init, childs_updated, self.considerRelType)

        if self.toConsole:
            print('')
            print("".ljust(indent*4) + 'children unchanged: {}'.format(similarity[0]))
            print("".ljust(indent*4) + 'children added: {}'.format(similarity[1]))
            print("".ljust(indent*4) + 'children deleted: {} \n'.format(similarity[2]))

        if (len(similarity[1]) != 0 or len(similarity[2]) != 0):
            diffContainer.isSimilar = False
            # log unsimilarities
            for addedNodeId in similarity[1]:
                diffContainer.logStructureModification(nodeId_init, addedNodeId, "added")
            for deletedNodeId in similarity[2]:
                diffContainer.logStructureModification(nodeId_updated, deletedNodeId, "deleted")

            return diffContainer

        # loop over all (similar) children
        for similarChild in similarity[0]: 
            # ToDo: log unchanged nodes if requested

            # trigger recursion
            diffContainer = self.__compareChildren(similarChild[0], similarChild[1], diffContainer, indent + 1)
            if diffContainer.isSimilar == False:
                return diffContainer

        return diffContainer


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
