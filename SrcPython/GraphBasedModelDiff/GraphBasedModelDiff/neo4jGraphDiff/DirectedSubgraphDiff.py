

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
        children_init = self.__getChildren(self.label_init, nodeId_init, indent +1)
        children_updated = self.__getChildren(self.label_updated, nodeId_updated, indent +1)

        
        matchOnRelType = []
        matchOnChildNodeType = []

        # option 1: match on relType and ignore nodeType
        matchOnRelType = self.__matchNodesOnRelType(children_init, children_updated)

        # option 2: match on nodeType and ignore relType (relevant for data models where the relType is not set)
        matchOnChildNodeType = self.__matchNodesOnEntityType(children_init, children_updated)
       
        # ToDo: implement some config options in the class constructor to trigger, which child matching method should be chosen
        match = matchOnRelType

        # check the nodes that have the same relationship OR the same EntityType and the same node type: 
        for candidate in match: 
            # compare two nodes
            cypher = neo4jQueryFactory.DiffNodes(nodeId_init, nodeId_updated)
            raw = self.connector.run_cypher_statement(cypher)
            diff = self.unpackNodeDiff(raw)

            # apply DiffIgnore on diff result 
            ignoreAttrs = self.utils.diffIngore.ignore_attrs
            diff_wouIgnore = self.__applyDiffIgnoreOnNodeDiff(diff, ignoreAttrs)

            print('comparing node {} to node {} after applying DiffIgnore:'.format(nodeId_init, nodeId_updated))
            print(diff_wouIgnore)


    def compareChildren(self, nodeId_init, nodeId_updated, isSimilar, indent = 0 ): 

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
            isSimilar = self.compareChildren(similarChild[0], similarChild[1], isSimilar, indent + 1)
            if isSimilar == False:
                return isSimilar

        return isSimilar

    def __getChildren(self, label, parentNodeId, indent = 0): 

        # queries all directed neighbors, their relType and their node hashes

        match = 'MATCH (n:{}) -[r]->(c)'.format(label)
        where = 'WHERE ID(n) = {}'.format(parentNodeId)
        ret = 'RETURN ID(c), type(r), c.entityType'

        cypher = neo4jUtils.BuildMultiStatement([match, where, ret])

        res_raw = self.connector.run_cypher_statement(cypher)

        res = self.__unpackChildren(res_raw)

       
        # check if leave node got touched
        if len(res) == 0:            
            return []
        else:
            return res

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

    def __matchNodesOnRelType(self, children_init, children_updated):
        """ compares two lists of ChildNodes and returns tuples of possible similar childs based on the same relType to the parent node """

        # init return list
        matchOnRelType = []

        # extract all relTypes
        all_relTypes_init = [x.relType for x in children_init] 
        all_relTypes_updated = [x.relType for x in children_updated] 

        # find relTypes used to connect initial child nodes in updated relTypes
        for ch in children_init:
            match_in_updated = ch.relType in all_relTypes_updated
            if match_in_updated == True: 
                ind = all_relTypes_updated.index(ch.relType)
                candidate = (ch, children_updated[ind])
                if candidate not in matchOnRelType:
                    matchOnRelType.append(candidate)

        # find relTypes used to connect updated child nodes in initial relTypes       
        for ch in children_updated:
            match_in_initial = ch.relType in all_relTypes_init
            if match_in_initial == True: 
                ind = all_relTypes_init.index(ch.relType)
                candidate = (children_init[ind], ch)

                if candidate not in matchOnRelType:
                    matchOnRelType.append(candidate)

        return matchOnRelType

    def __matchNodesOnEntityType(self, children_init, children_updated): 
        """ compares two lists of ChildNodes and returns tuples of possible similar childs based on the same entityType """

        # init return list
        matchOnEntityType = []
        
         # extract all relTypes
        all_EntityTypes_init = [x.entityType for x in children_init] 
        all_EntityTypes_updated = [x.entityType for x in children_updated] 

        # find relTypes used to connect initial child nodes in updated relTypes
        for ch in children_init:
            match_in_updated = ch.entityType in all_EntityTypes_updated
            if match_in_updated == True: 
                ind = all_EntityTypes_updated.index(ch.entityType)
                candidate = (ch, children_updated[ind])

                if candidate not in matchOnEntityType:
                    matchOnEntityType.append(candidate)

        # find relTypes used to connect updated child nodes in initial relTypes       
        for ch in children_updated:
            match_in_initial = ch.entityType in all_EntityTypes_init
            if match_in_initial == True: 
                ind = all_EntityTypes_init.index(ch.entityType)
                candidate = (children_init[ind], ch)

                if candidate not in matchOnEntityType:
                    matchOnEntityType.append(candidate)

        return matchOnEntityType

# -- Helper Functions --- 
    def __unpackChildren(self, result): 
        ret_val = []
        for res in result: 
            child = ChildData(res[0], res[1], res[2]) 
            ret_val.append(child)
        return ret_val

    def unpackNodeDiff(self, result):
        ret_val = NodeDiff(result[0][0]['inCommon'], result[0][0]['different'],result[0][0]['rightOnly'], result[0][0]['leftOnly'] )
        return ret_val

    def __applyDiffIgnoreOnNodeDiff(self, diff, IgnoreAttrs): 

        for ignore in IgnoreAttrs:
            if ignore in diff.AttrsUnchanged:       del diff.AttrsUnchanged[ignore]
            if ignore in diff.AttrsAdded:           del diff.AttrsAdded[ignore]
            if ignore in diff.AttrsDeleted:         del diff.AttrsDeleted[ignore]
            if ignore in diff.AttrsModified:        del diff.AttrsModified[ignore]


        return diff


class ChildData(): 
    def __init__(self, id, relType, entityType= None):
        self.id = id
        self.entityType = entityType
        self.hash = None
        self.relType = relType
        
    def setHash(self, hash): 
        self.hash = hash

    def __repr__(self):
        return 'ChildData: id: {} nodeType: {} relType = {} hash: {}'.format(self.id, self.NodeType, self.relType, self.hash)


class NodeDiff(): 
    def __init__(self, unchanged, modified, added, deleted): 
        self.AttrsUnchanged = unchanged
        self.AttrsModified = modified
        self.AttrsAdded = added
        self.AttrsDeleted = deleted


    def __str__(self): 
        print('unchanged: {}'.format(self.AttrsUnchanged))
        print('modified: {}'.format(self.AttrsModified))
        print('added: {}'.format(self.AttrsAdded))
        print('deleted: {}'.format(self.AttrsDeleted))
        