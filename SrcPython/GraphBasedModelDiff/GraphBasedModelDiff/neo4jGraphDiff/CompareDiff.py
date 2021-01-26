
import abc

from .DirectedSubgraphDiff import DirectedSubgraphDiff
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory
from neo4j_middleware.NodeDiffData import NodeDiffData
from neo4j_middleware.NodeData import NodeData
from .DiffResult import DiffResult

from neo4jGraphDiff.DiffResult import DiffResult 


class CompareDiff(DirectedSubgraphDiff):
    """ compares two directed subgraphs based on a node diff of nodes and recursively analyses the entire subgraph """ 
    
    def __init__(self, connector, label_init, label_updated, config):
        
        return super().__init__(connector, label_init, label_updated, config)
    
    # public overwrite method requested by abstract superclass DirectedSubgraphDiff
    def diffSubgraphs(self, node_init, node_updated): 

        diffContainer = DiffResult(method = "Node-Diff")
      
        # start recursion
        diffContainer = self.__compareChildren(node_init, node_updated, diffContainer)
        return diffContainer


    def __compareChildren(self, node_init, node_updated, diffResultContainer, indent=0): 
        """ queries the all child nodes of a node and compares the results between the initial and the updated graph based on AttrDiff"""
        # get children data

        # --- 1 --- query all childs of current node 
        children_init =     self._DirectedSubgraphDiff__getChildren(self.label_init, node_init.id,    indent +1)
        children_updated =  self._DirectedSubgraphDiff__getChildren(self.label_updated, node_updated.id, indent +1)

        # leave node?
        if len(children_init) == 0 and len(children_updated) == 0: 
            if self.toConsole():
                print("".ljust(indent*4) + ' leaf node.')
            return diffResultContainer

        # apply DiffIgnore -> Ignore nodes if requested        
        children_init = self._DirectedSubgraphDiff__applyDiffIgnore_Nodes(children_init)
        children_updated = self._DirectedSubgraphDiff__applyDiffIgnore_Nodes(children_updated)

        # --- 2 --- match detected child nodes based on a chosen method 

        desiredMatchMethod = self.configuration.DiffSettings.MatchingType_Childs
        # ToDo switch here to apply the correct method

        matchOnRelType = []
        matchOnChildNodeType = []

        # option 1: match on relType and ignore nodeType
        matchOnRelType = self.__matchNodesOnRelType(children_init, children_updated)

        # option 2: match on nodeType and ignore relType (relevant for data models where the relType is not set)
        matchOnChildNodeType = self.__matchNodesOnEntityType(children_init, children_updated)
       
        # ToDo: implement some config options in the class constructor to trigger, which child matching method should be chosen
        # match = matchOnChildNodeType
        match = matchOnRelType

        # --- 3 --- loop over all matching child pairs and detect their similarities and differences

        # check the nodes that have the same relationship OR the same EntityType and the same node type: 
        for matchingChilds in match: 
            # compare two nodes
            cypher = neo4jQueryFactory.DiffNodes(matchingChilds[0].id, matchingChilds[1].id) # compare childs? or current node?
            raw = self.connector.run_cypher_statement(cypher)
            #diff = self.unpackNodeDiff(raw)
            nodeDifference = NodeDiffData.fromNeo4jResponse(raw)

            # apply DiffIgnore on diff result 
            ignoreAttrs = self.configuration.DiffSettings.diffIgnoreAttrs
            cleared_nodeDifference = self.__applyDiffIgnoreOnNodeDiff(nodeDifference, ignoreAttrs)

            if self.toConsole():
                print('comparing node {} to node {} after applying DiffIgnore:'.format(node_init.id, node_updated.id))
           
            # case 1: no modifications on pair
            if cleared_nodeDifference.nodesAreSimilar() == True: 
                # nodes are similar
                if self.toConsole():
                    print('[RESULT]: child nodes match')
               
            
            # case 2: modified attrs on pair but no added/deleted attrs
            elif cleared_nodeDifference.nodesHaveUpdatedAttrs() == True: 
                diffResultContainer.isSimilar = False

                for modifiedAttr in cleared_nodeDifference.AttrsModified.items():
                    if self.toConsole():
                        print(modifiedAttr)

                    # ToDo: move extraction of data from tuple to higher representation
                    attr_name = modifiedAttr[0]
                    val_old = modifiedAttr[1]['left']
                    val_new = modifiedAttr[1]['right']

                    diffResultContainer.logNodeModification(node_init.id,node_updated.id , attr_name, 'modified', val_old, val_new)                           

            # case 3: added/deleted attrs. Break recursion
            else:
                if self.toConsole():
                    print('[RESULT]: detected unsimilarity between nodes {} and {}'.format(node_init.id, node_updated.id))
                    print(cleared_nodeDifference)
                # log result
                diffResultContainer.isSimilar = False
                
                # log modified
                for modAttr in cleared_nodeDifference.AttrsModified.items(): 
                    attr_name = modAttr[0]
                    val_old = modAttr[1]['left']
                    val_new = modAttr[1]['right']
                    diffResultContainer.logNodeModification(node_init.id, node_updated.id , attr_name, 'modified', val_old, val_new)    

                # log added
                for addedAttr in cleared_nodeDifference.AttrsAdded.items():
                    attr_name = addedAttr[0]
                    val_new = addedAttr[1]
                    diffResultContainer.logNodeModification(None, node_updated.id , attr_name, 'added', None, val_new)  
                
                # log deleted
                for delAttr in cleared_nodeDifference.AttrsDeleted.items():
                    attr_name = delAttr[0]
                    val_new = delAttr[1]
                    diffResultContainer.logNodeModification(node_init.id, None , attr_name, 'deleted', val_old, None)  

                return diffResultContainer


            # run recursion for children if "NoChange" or "Modified" happened
            diffResultContainer = self.__compareChildren(matchingChilds[0], matchingChilds[1], diffResultContainer)
            
            # end for loop 

        return diffResultContainer

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
