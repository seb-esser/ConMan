
    
import abc

from .DirectedSubgraphDiff import DirectedSubgraphDiff


class HashDiff(DirectedSubgraphDiff):
    """description of class"""

    def __init__(self, connector, label_init, label_updated, diffIgnorePath=None):
        return super().__init__(connector, label_init, label_updated, diffIgnorePath=diffIgnorePath)
    
    def diffSubgraphs(self, nodeId_init, nodeId_updated): 

        # ToDo: return diff results and not only True/False in case of a spotted difference between init and updated
        isSimilar = True
        isSimilar = self.__compareChildren(nodeId_init, nodeId_updated, isSimilar)
        return isSimilar

    # compare children method. recursive usage

    def __compareChildren(self, nodeId_init, nodeId_updated, isSimilar, indent = 0 ): 
        """  queries the all child nodes of a node and compares the results between the initial and the updated graph based on hash comparison """

        # get children data
        children_init = self.__getChildren(self.label_init, nodeId_init, indent +1)
        children_updated = self.__getChildren(self.label_updated, nodeId_updated, indent +1)

        # leave node
        if len(children_init) == 0 and len(children_updated) == 0: 
            print('- - - ')
            return isSimilar

        # calc hashes for init and updated
        childs_init = self.__getHashesOfNodes(self.label_init, children_init)
        childs_updated = self.__getHashesOfNodes(self.label_updated, children_updated)

        # compare children and raise an unsimilarity if necessary.
        similarity = self.utils.CompareNodesByHash(childs_init, childs_updated)

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
        # calc corresponding hash
        for node in nodeList: 
            child_node_id = node.id
            relType = node.relType
            # calc hash of current node
            cypher_hash = neo4jUtils.BuildMultiStatement(self.utils.GetHashByNodeId(label, child_node_id))
            hash = self.connector.run_cypher_statement(cypher_hash)[0][0]

            node.setHash(hash)

           
        return nodeList
