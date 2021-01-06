

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

        self.compareChildrenOnDiff(nodeId_init, nodeId_updated)

        


    def compareChildrenOnDiff(self, nodeId_init, nodeId_updated, indent=0): 

        # get children data
        children_init = self.getChildren(self.label_init, nodeId_init, indent +1)
        children_updated = self.getChildren(self.label_updated, nodeId_updated, indent +1)

        # match possible similar nodes based on relType and children nodeType:
        all_options = [(x, y) for x in children_init for y in children_updated]

        match = []

        # - note 2021-01-06: continue here

        for candidate in all_options:
            if ( candidate[0] == candidate[1] ):
                # same node type and same relationship
                match.append(candidate)


        # check the nodes that have the same relationship and the same node type: 
        for candidate in match: 
            # compare two nodes
            cypher = neo4jQueryFactory.DiffNodes(nodeId_init, nodeId_updated)
            raw = self.connector.run_cypher_statement(cypher)
            diff = self.unpackNodeDiff(raw)

            # apply DiffIgnore on diff result 
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
        childs_init = self.getHashesOfNodes(self.label_init, children_init)
        childs_updated = self.getHashesOfNodes(self.label_updated, children_updated)

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
            child_node_id = node.id
            relType = node.type
            # calc hash of current node
            cypher_hash = neo4jUtils.BuildMultiStatement(self.utils.GetHashByNodeId(label, child_node_id))
            hash = self.connector.run_cypher_statement(cypher_hash)[0][0]

            node.setHash(hash)

            #ret_obj = {}
            #ret_obj['nodeId'] = child_node_id
            #ret_obj['relType'] = relType
            #ret_obj['hash'] = hash
            #return_val.append(ret_obj)

        return nodeList

# -- Helper Functions --- 
    def unpackChildren(self, result): 
        ret_val = []
        for res in result: 
            child = ChildData(res[0], res[1]) 
            ret_val.append(child)
        return ret_val

    def unpackNodeDiff(self, result):
        ret_val = NodeDiff(result[0][0]['inCommon'], result[0][0]['different'],result[0][0]['rightOnly'], result[0][0]['leftOnly'] )
        return ret_val

    def applyDiffIgnoreOnNodeDiff(self, diff, IgnoreAttrs): 

        for ignore in IgnoreAttrs:
            if ignore in diff['AttrsUnchanged'].keys(): del diff['AttrsUnchanged'][ignore]
            if ignore in diff['AttrsAdded'].keys(): del diff['AttrsAdded'][ignore]
            if ignore in diff['AttrsDeleted'].keys(): del diff['AttrsDeleted'][ignore]
            if ignore in diff['AttrsModified'].keys(): del diff['AttrsModified'][ignore]


        return diff


class ChildData(): 
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.hash = None
        
    def setHash(self, hash): 
        self.hash = hash

    def __repr__(self):
        return 'ChildData: id: {} type: {} hash: {}'.format(self.id, self.type, self.hash)


class NodeDiff(): 
    def __init__(self, unchanged, modified, added, deleted): 
        self.AttrsUnchanged = unchanged
        self.AttrsModified = modified
        self.AttrsAdded = added
        self.AttrsDeleted = deleted
