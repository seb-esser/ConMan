

from .DiffUtilities import DiffUtilities
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils



class DirectedSubgraphDiff:
    """description of class"""


    def __init__(self, label_init, label_updated): 
        self.utils = DiffUtilities()
        self.label_init = label_init
        self.label_updated = label_updated
        


    def compareChildren(self, connector, nodeId_init, nodeId_updated, isSimilar, indent = 0 ): 

        # get children data
        children_init = self.getChildren(connector, self.label_init, nodeId_init, indent +1)
        children_updated = self.getChildren(connector, self.label_updated,nodeId_updated, indent +1)

        # leave node
        if len(children_init) == 0 and len(children_updated) == 0: 
            print('- - - ')
            return 

        # compare children and raise an unsimilarity if necessary.
        init_dict = {}
        updated_dict = {}
        for ch in children_init: 
            init_dict[ch['hash'] ] = ch['nodeId']
        for ch in children_updated: 
            updated_dict[ch['hash'] ] = ch['nodeId']

        similarity = self.utils.CompareNodesByHash(init_dict, updated_dict)
        print("".ljust(indent*4) + 'children unchanged: {}'.format(similarity[0]))
        print("".ljust(indent*4) + 'children added: {}'.format(similarity[1]))
        print("".ljust(indent*4) + 'children deleted: {}'.format(similarity[2]))

        if (len(similarity[1]) != 0 or len(similarity[2]) != 0):
            isSimilar = False
            return isSimilar

        # loop over all (similar) children
        for similarChild in similarity[0]: 
            isSimilar = self.compareChildren(connector, similarChild[0], similarChild[1], isSimilar, indent + 1)
            if isSimilar == False:
                return isSimilar

        return isSimilar

    def getChildren(self, connector, label, parentNodeId, indent = 0): 

        # queries all directed neighbors, their relType and their node hashes

        match = 'MATCH (n:{}) -[r]->(c)'.format(label)
        where = 'WHERE ID(n) = {}'.format(parentNodeId)
        ret = 'RETURN ID(c), type(r)'

        cypher = neo4jUtils.BuildMultiStatement([match, where, ret])

        res_raw = connector.run_cypher_statement(cypher)

        res = self.unpackChildren(res_raw)

        return_val = []
        # calc corresponding hash
        for node in res: 
            child_node_id = node[0]
            relType = node[1]
            # calc hash of current node
            cypher_hash = neo4jUtils.BuildMultiStatement(self.utils.GetHashByNodeId(label, child_node_id))
            hash = connector.run_cypher_statement(cypher_hash)[0][0]
            ret_obj = {}
            ret_obj['nodeId'] = child_node_id
            ret_obj['relType'] = relType
            ret_obj['hash'] = hash
            return_val.append(ret_obj)

        # check if leave node got touched
        if len(res) == 0:            
            return []
        else:
            return return_val


# -- Helper Functions --- 
    def unpackChildren(self, result): 
        return_val = []
        for res in result: 
            childId = res[0]
            relType = res[1]
            return_val.append( (childId, relType) )
        return return_val