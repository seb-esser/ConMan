

from .DiffUtilities import DiffUtilities
from neo4j_middleware.neo4jQueryUtilities import neo4jQueryUtilities as neo4jUtils
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory



class DirectedSubgraphDiff:
    """description of class"""


    def __init__(self, connector, label_init, label_updated, diffIgnorePath = None): 

        if diffIgnorePath != None:
            self.utils = DiffUtilities(diffIgnorePath)
            self.UseDiffIgnore = True
        else: 
            self.UseDiffIgnore = False

        self.connector = connector
        self.label_init = label_init
        self.label_updated = label_updated
        
    
    """ compares two directed subgraphs based on the fingerprint of nodes and recursively analyses the entire subgraph """ 
    def diffSubgraphsOnHash(self, nodeId_init, nodeId_updated):
        
        isSimilar = True
        isSimilar = self.compareChildren(nodeId_init, nodeId_updated, isSimilar, 0)
        return isSimilar


    """ compares two directed subgraphs based on a node diff of nodes and recursively analyses the entire subgraph """ 
    def diffSubgraphsOnCompare(self,  nodeId_init, nodeId_updated): 

        # compare two nodes
        cypher = neo4jQueryFactory.DiffNodes(nodeId_init, nodeId_updated)
        raw = self.connector.run_cypher_statement(cypher)
        diff = self.unpackNodeDiff(raw)

        # apply DiffIgnore
        ignoreAttrs = self.utils.diffIngore.ignore_attrs
        diff_wouIgnore = self.applyDiffIgnoreOnNodeDiff(diff, ignoreAttrs)



    def compareChildren(self, nodeId_init, nodeId_updated, isSimilar, indent = 0 ): 

        # get children data
        children_init = self.getChildren(self.label_init, nodeId_init, indent +1)
        children_updated = self.getChildren(self.label_updated, nodeId_updated, indent +1)

        # leave node
        if len(children_init) == 0 and len(children_updated) == 0: 
            print('- - - ')
            return isSimilar

        # calc hashes for init and updated
        hashes_ch_init = self.getHashesOfNodes(self.label_init, children_init)
        hashes_ch_updated = self.getHashesOfNodes(self.label_updated, children_updated)

        # compare children and raise an unsimilarity if necessary.
        init_dict = {}
        updated_dict = {}
        for ch in hashes_ch_init: 
            init_dict[ch['hash'] ] = ch['nodeId']
        for ch in hashes_ch_updated: 
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
            isSimilar = self.compareChildren(similarChild[0], similarChild[1], isSimilar, indent + 1)
            if isSimilar == False:
                return isSimilar

        return isSimilar

    def getChildren(self, label, parentNodeId, indent = 0): 

        # queries all directed neighbors, their relType and their node hashes

        match = 'MATCH (n:{}) -[r]->(c)'.format(label)
        where = 'WHERE ID(n) = {}'.format(parentNodeId)
        ret = 'RETURN ID(c), type(r)'

        cypher = neo4jUtils.BuildMultiStatement([match, where, ret])

        res_raw = self.connector.run_cypher_statement(cypher)

        res = self.unpackChildren(res_raw)

       
        # check if leave node got touched
        if len(res) == 0:            
            return []
        else:
            return res

    def getHashesOfNodes(self, label, nodeList):
        return_val = []
        # calc corresponding hash
        for node in nodeList: 
            child_node_id = node[0]
            relType = node[1]
            # calc hash of current node
            cypher_hash = neo4jUtils.BuildMultiStatement(self.utils.GetHashByNodeId(label, child_node_id))
            hash = self.connector.run_cypher_statement(cypher_hash)[0][0]
            ret_obj = {}
            ret_obj['nodeId'] = child_node_id
            ret_obj['relType'] = relType
            ret_obj['hash'] = hash
            return_val.append(ret_obj)

        return return_val

# -- Helper Functions --- 
    def unpackChildren(self, result): 
        ret_val = []
        for res in result: 
            childId = res[0]
            relType = res[1]
            ret_val.append( (childId, relType) )
        return ret_val

    def unpackNodeDiff(self, result):
        ret_val = {}
        ret_val['AttrsUnchanged'] = result[0][0]['inCommon']
        ret_val['AttrsModified']  = result[0][0]['different']
        ret_val['AttrsAdded']  =    result[0][0]['rightOnly']
        ret_val['AttrsDeleted']  =  result[0][0]['leftOnly']

        return ret_val

    def applyDiffIgnoreOnNodeDiff(self, diff, IgnoreAttrs): 

        for ignore in IgnoreAttrs:
            if ignore in diff['AttrsUnchanged'].keys(): del diff['AttrsUnchanged'][ignore]
            if ignore in diff['AttrsAdded'].keys(): del diff['AttrsAdded'][ignore]
            if ignore in diff['AttrsDeleted'].keys(): del diff['AttrsDeleted'][ignore]
            if ignore in diff['AttrsModified'].keys(): del diff['AttrsModified'][ignore]


        return diff