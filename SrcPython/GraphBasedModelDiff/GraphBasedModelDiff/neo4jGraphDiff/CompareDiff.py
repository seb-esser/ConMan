
import abc

from .DirectedSubgraphDiff import DirectedSubgraphDiff
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory
from neo4j_middleware.NodeDiffData import NodeDiffData


class CompareDiff(DirectedSubgraphDiff):
    """ compares two directed subgraphs based on a node diff of nodes and recursively analyses the entire subgraph """ 
    
    def __init__(self, connector, label_init, label_updated, diffIgnorePath=None, toConsole = False):
        self.toConsole = False
        return super().__init__(connector, label_init, label_updated, diffIgnorePath=diffIgnorePath)
    
    # public overwrite method requested by abstract superclass DirectedSubgraphDiff
    def diffSubgraphs(self, nodeId_init, nodeId_updated): 

        # ToDo: return diff results and not only True/False in case of a spotted difference between init and updated
        isSimilar = True
        isSimilar = self.__compareChildren(nodeId_init, nodeId_updated, isSimilar)
        return isSimilar


    def __compareChildren(self, nodeId_init, nodeId_updated, isSimilar, indent=0): 
        """ queries the all child nodes of a node and compares the results between the initial and the updated graph based on AttrDiff"""
        # get children data
        self._DirectedSubgraphDiff__getChildren
        children_init =     self._DirectedSubgraphDiff__getChildren(self.label_init,    nodeId_init, indent +1)
        children_updated =  self._DirectedSubgraphDiff__getChildren(self.label_updated, nodeId_updated, indent +1)

        # leave node?
        if len(children_init) == 0 and len(children_updated) == 0: 
            if self.toConsole:
                print('- - - ')
            return isSimilar

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
            #diff = self.unpackNodeDiff(raw)
            diff = NodeDiffData.fromNeo4jResponse(raw)

            # apply DiffIgnore on diff result 
            ignoreAttrs = self.utils.diffIngore.ignore_attrs
            diff_wouIgnore = self.__applyDiffIgnoreOnNodeDiff(diff, ignoreAttrs)

            if self.toConsole:
                print('comparing node {} to node {} after applying DiffIgnore:'.format(nodeId_init, nodeId_updated))
           
            if diff_wouIgnore: 
                # nodes are similar
                if self.toConsole:
                    print('[RESULT]: child nodes match')

                # run recursion
                self.__compareChildren(candidate[0].id, candidate[1].id, isSimilar)

            else:
                if self.toConsole:
                    print('[RESULT]: detected unsimilarity between nodes {} and {}').format(nodeId_init, nodeId_updated)
                    print(diff_wouIgnore)

                isSimilar = False
                return False
            
        return isSimilar

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

    def __applyDiffIgnoreOnNodeDiff(self, diff, IgnoreAttrs): 
        """ removes the attributes stated in the used DiffIgnore file from the diff result of apoc """ 
        for ignore in IgnoreAttrs:
            if ignore in diff.AttrsUnchanged:       del diff.AttrsUnchanged[ignore]
            if ignore in diff.AttrsAdded:           del diff.AttrsAdded[ignore]
            if ignore in diff.AttrsDeleted:         del diff.AttrsDeleted[ignore]
            if ignore in diff.AttrsModified:        del diff.AttrsModified[ignore]


        return diff