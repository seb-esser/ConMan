
import abc

from .DirectedSubgraphDiff import DirectedSubgraphDiff
from neo4j_middleware.neo4jQueryFactory import neo4jQueryFactory
from neo4j_middleware.NodeDiffData import NodeDiffData
from neo4j_middleware.NodeData import NodeData
from .DiffResult import DiffResult

from neo4jGraphDiff.DiffResult import DiffResult 
from neo4jGraphDiff.ConfiguratorEnums import MatchCriteriaEnum

class DepthFirstSearchComparison(DirectedSubgraphDiff):
    """ compares two directed subgraphs based on a node diff of nodes and recursively analyses the entire subgraph """ 
    
    def __init__(self, connector, label_init, label_updated, config):
        
        return super().__init__(connector, label_init, label_updated, config)
    
    # public overwrite method requested by abstract superclass DirectedSubgraphDiff
    def diffSubgraphs(self, node_init, node_updated): 

        diffContainer = DiffResult(method = "Node-Diff", root_init = node_init, root_updated=node_updated)
               
        # start recursion
        diffContainer = self.__compareChildren(node_init, node_updated, diffContainer)
        return diffContainer


    

    def __compareChildren(self, node_init, node_updated, diffResultContainer, indent=0): 
        """ queries the all child nodes of a node and compares the results between the initial and the updated graph based on AttrDiff"""
        
        desiredMatchMethod = self.configuration.DiffSettings.MatchingType_Childs

        diffResultContainer.increaseRecursionCounter()

        if self.toConsole():
            print("".ljust(indent*4) + 'Check children of NodeId {} and NodeId {}'.format(node_init.id, node_updated.id))

        
        # get children data
        children_init =     self._DirectedSubgraphDiff__getChildren(self.label_init, node_init.id,    indent +1)
        children_updated =  self._DirectedSubgraphDiff__getChildren(self.label_updated, node_updated.id, indent +1)

        # leave node?
        if len(children_init) == 0 and len(children_updated) == 0: 
            if self.toConsole():
                print("".ljust(indent*4) + ' leaf node.')
            return diffResultContainer

        # calc hashes if necessary for matching method
        if desiredMatchMethod == MatchCriteriaEnum.OnHash:
            # calc hashes for init and updated
            childs_init = self.__getHashesOfNodes(self.label_init, children_init, indent)
            childs_updated = self.__getHashesOfNodes(self.label_updated, children_updated, indent)

        # apply DiffIgnore -> Ignore nodes if requested        
        children_init = self._DirectedSubgraphDiff__applyDiffIgnore_Nodes(children_init)
        children_updated = self._DirectedSubgraphDiff__applyDiffIgnore_Nodes(children_updated)

        # compare children and raise an unsimilarity if necessary.
        [nodes_unchanged, nodes_added, nodes_deleted] = self.utils.CompareNodes(children_init, children_updated, desiredMatchMethod) 
        
        if self.toConsole():
            print('')
            print("".ljust(indent*4) + 'children unchanged: {}'.format(nodes_unchanged))
            print("".ljust(indent*4) + 'children added: {}'.format(nodes_added))
            print("".ljust(indent*4) + 'children deleted: {} \n'.format(nodes_deleted))

        if (len(nodes_added) != 0 or len(nodes_deleted) != 0):
            # log structural modifications
            for ch in nodes_added:
                diffResultContainer.logStructureModification(node_updated.id, ch.id, 'added')
            
            for ch in nodes_deleted:
                diffResultContainer.logStructureModification(node_init.id, ch.id, 'deleted')
            


        # --- 3 --- loop over all matching child pairs and detect their similarities and differences

        # check the nodes that have the same relationship OR the same EntityType and the same node type: 
        for matchingChildPair in nodes_unchanged: 
                        
            # detect changes on property level between both matching nodes
            diffResultContainer = self.__calcPropertyDifference(diffResultContainer, matchingChildPair, node_init, node_updated)  
            
            # run recursion for children if "NoChange" or "Modified" happened
            diffResultContainer = self.__compareChildren(matchingChildPair[0], matchingChildPair[1], diffResultContainer)
            
            # end for loop 

        return diffResultContainer


    def __applyDiffIgnoreOnNodeDiff(self, diff, IgnoreAttrs): 
        """ removes the attributes stated in the used DiffIgnore file from the diff result of apoc """ 
        for ignore in IgnoreAttrs:
            if ignore in diff.AttrsUnchanged:       del diff.AttrsUnchanged[ignore]
            if ignore in diff.AttrsAdded:           del diff.AttrsAdded[ignore]
            if ignore in diff.AttrsDeleted:         del diff.AttrsDeleted[ignore]
            if ignore in diff.AttrsModified:        del diff.AttrsModified[ignore]


        return diff

    def __calcPropertyDifference(self, diffResultContainer, matchingChildPair, node_init, node_updated):
    	""" runs an analyis on node properties to detect property Modifications """    	
    	
        # compare two nodes
    	cypher = neo4jQueryFactory.DiffNodes(matchingChildPair[0].id, matchingChildPair[1].id) # compare childs? or current node?
    	raw = self.connector.run_cypher_statement(cypher)
    	
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
    	    
    	    # log modification
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
    	    
    	    # -- log result --
    	                    
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


    def __getHashesOfNodes(self, label, nodeList, indent = 0):
        return_val = []

        ignore_attrs = self.configuration.DiffSettings.diffIgnoreAttrs # list of strings
        # calc corresponding hash
        for node in nodeList: 
            child_node_id = node.id
            relType = node.relType
            # calc hash of current node
            cypher_hash = neo4jQueryFactory.GetHashByNodeId(label, child_node_id, ignore_attrs )
            hash = self.connector.run_cypher_statement(cypher_hash)[0][0]

            node.setHash(hash)

        if self.toConsole(): 
            print("".ljust(indent*4) + 'Calculated hashes for model >> {} <<:'.format(label))
            for node in nodeList:
                print("".ljust(indent*4) + '\t NodeID: {:<4} \t hash: {}'.format(node.id, node.hash))


        return nodeList