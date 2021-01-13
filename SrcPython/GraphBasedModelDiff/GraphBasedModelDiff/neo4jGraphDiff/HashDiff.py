
    
import abc

from .DirectedSubgraphDiff import DirectedSubgraphDiff
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils


class HashDiff(DirectedSubgraphDiff):
    """description of class"""

    def __init__(self, connector, label_init, label_updated, diffIgnorePath=None, LogtoConsole = False):
        
        return super().__init__(connector, label_init, label_updated, diffIgnorePath=diffIgnorePath, toConsole=LogtoConsole)
    
    def diffSubgraphs(self, nodeId_init, nodeId_updated): 

        # ToDo: return diff results and not only True/False in case of a spotted difference between init and updated
        isSimilar = True
        isSimilar = self.__compareChildren(nodeId_init, nodeId_updated, isSimilar)
        return isSimilar

    # compare children method. recursive usage

    def __compareChildren(self, nodeId_init, nodeId_updated, isSimilar, indent = 0 ): 
        """  queries the all child nodes of a node and compares the results between the initial and the updated graph based on hash comparison """

        # get children data
        children_init =     self._DirectedSubgraphDiff__getChildren(self.label_init, nodeId_init, indent +1)
        children_updated =  self._DirectedSubgraphDiff__getChildren(self.label_updated, nodeId_updated, indent +1)

        # leave node
        if len(children_init) == 0 and len(children_updated) == 0: 
            if self.toConsole:
                print('- - - ')
            return isSimilar

        # calc hashes for init and updated
        childs_init = self.__getHashesOfNodes(self.label_init, children_init)
        childs_updated = self.__getHashesOfNodes(self.label_updated, children_updated)

        # apply DiffIgnore -> Ingore nodes if requested
        if self.UseDiffIgnore: 
            children_init = self._DirectedSubgraphDiff__applyDiffIgnore_Nodes(children_init)
            children_updated = self._DirectedSubgraphDiff__applyDiffIgnore_Nodes(children_updated)


        # compare children and raise an unsimilarity if necessary.
        similarity = self.utils.CompareNodesByHash(childs_init, childs_updated)
        if self.toConsole:
            print("".ljust(indent*4) + 'children unchanged: {}'.format(similarity[0]))
            print("".ljust(indent*4) + 'children added: {}'.format(similarity[1]))
            print("".ljust(indent*4) + 'children deleted: {}'.format(similarity[2]))

        if (len(similarity[1]) != 0 or len(similarity[2]) != 0):
            isSimilar = False
            return isSimilar

        # loop over all (similar) children
        for similarChild in similarity[0]: 
            isSimilar = self.__compareChildren(similarChild[0], similarChild[1], isSimilar, indent + 1)
            if isSimilar == False:
                return isSimilar

        return isSimilar


    def __getHashesOfNodes(self, label, nodeList):
        return_val = []

        ignore_attrs = self.utils.diffIngore.ignore_attrs

        # calc corresponding hash
        for node in nodeList: 
            child_node_id = node.id
            relType = node.relType
            # calc hash of current node
            cypher_hash = neo4jUtils.BuildMultiStatement(self.utils.GetHashByNodeId(label, child_node_id, ignore_attrs ))
            hash = self.connector.run_cypher_statement(cypher_hash)[0][0]

            node.setHash(hash)

        if self.toConsole: 
            print('Calculated hashes for model >> {} <<:'.format(label))
            for node in nodeList:
                print('\t NodeID: {:<4} \t hash: {}'.format(node.id, node.hash))


        return nodeList
