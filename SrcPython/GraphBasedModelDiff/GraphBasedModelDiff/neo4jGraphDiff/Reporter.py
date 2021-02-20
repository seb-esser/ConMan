

""" package import """


""" module import """
from neo4jGraphDiff.DiffResult import DiffResult

""" class def """
class Report:
    """description of class"""

    def __init__(self, result = None, usedConfig = None):
        """ """
        self.result = result
        self.config = usedConfig

        self.ResultRooted = {}
        self.ResultComponentDiff = []


    def CaptureResult_RootedDiff(self, rootDiffRes):
        """ captures DiffResult of RootedDiff"""
        nodes_unchanged = rootDiffRes[0]
        nodes_added = rootDiffRes[1]
        nodes_deleted = rootDiffRes[2]

        self.ResultRooted['unchanged'] = nodes_unchanged
        self.ResultRooted['added'] = nodes_added
        self.ResultRooted['deleted'] = nodes_deleted                          

    def CaptureResult_ObjRels(self):
        """ captures DiffResult of ObjRel structure Diff """
        pass

    def CaptureResult_ComponentDiff(self, diffRes): 
        """ captures DiffResult of a componentDiff """
        self.ResultComponentDiff.append(diffRes)


    def printResultToConsole(self):
        print('--- --- --- --- --- --- --- --- --- ')
        print('--- --- REPORT  --- --- --- --- --- \n')
    
        print('Applied Config: ')
        print(self.config)
        
        print('\n _______ ROOT STRUCTURE ______________')

        print('\nROOT NODES:')
        
        print('\t NODES-PAIRS UNCHANGED: ')
        for item in self.ResultRooted['unchanged']:
            print('\t  init: NodeId:{:<5} EntityType: {:<20} updated: NodeId:{:<5} EntityType: {:<20}'.format(item[0].id, item[0].entityType, item[1].id, item[1].entityType))

        print('\n\t NODES ADDED:')
        if len(self.ResultRooted['added']) > 0:
            for item in self.ResultRooted['added']:
                print('\t  NodeId:{:<5} EntityType: {:<20}'.format(item.id, item.entityType))
        else:
            print('\t  EMPTY')


        print('\n\t NODES DELETED:')
        if len(self.ResultRooted['deleted']) > 0:
            for item in self.ResultRooted['deleted']:
                print('\t  NodeId:{:<5} EntityType: {:<20}'.format(item.id, item.entityType))
        else:
            print('\t  EMPTY')

        
        #print('\nROOT RELATIONSHIPS:')

        
        print('\n _______ COMPONENT STRUCTURE ____________')

        for item in self.ResultComponentDiff:
            print('\t NodePair: init: {:<5} updated: {:<5}'.format(item.RootNode_init.id, item.RooteNode_updated.id))
            print('\t  Time: {}'.format(item.time))
            if item.isSimilar:
                print('\t  Unchanged: TRUE')
            else: 
                print('\t  Unchanged: FALSE')

            if not item.isSimilar:
                for res in item.propertyModifications:
                    print('\t   PropertyMod: NodeId_INIT: {:<5} NodeId_UPDATED: {:<5}'.format(res.nodeId_init, res.nodeId_updated))
                    print('\t    |-> ModificationType: {:<15} oldValue: {:<10} newValue: {:<10}'.format(res.modificationType, res.valueOld, res.valueNew))
                
                for res in item.StructureModifications:
                    print('\t   StructuralMod: NodeId_PARENT: {:<5} NodeId_Child: {:<5}'.format(res.parentId, res.childId))
                    print('\t    |-> ModificationType: {:<15} '.format(res.modType))
            print()



    def __str__(self):
        """ dunder method to pretty print the Reporter object object to console. If results are intented, use print(inst.result)""" 
        pass


    def reportToJSON(self):
        """ formats the result object into a nice json object and returns the json string """
        pass 





