

""" package import """
import matplotlib.pyplot as plt
import numpy as np

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
        print('\n')
        print('--- --- --- --- --- --- --- --  --- --- --- --- --- --- ')
        print('--- --- --- --- --- --- REPORT  --- --- --- --- --- --- \n')
        print('--- --- --- --- --- --- --- --  --- --- --- --- --- --- ')
    
        print('Applied Config: ')
        print(self.config)
        
        print('\n _______ ROOT STRUCTURE ______________')

        print('\nROOT NODES:')
        
        print('\t NODES-PAIRS UNCHANGED: ')
        for item in self.ResultRooted['unchanged']:
            print('\t  init: NodeId:{:<5} EntityType: {:<26} updated: NodeId:{:<5} EntityType: {:<26}'.format(item[0].id, item[0].entityType, item[1].id, item[1].entityType))

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

        
        print('\nROOT OBJ RELATIONSHIPS:')
        print()

        
        print('\n _______ COMPONENT STRUCTURE ____________')

        for item in self.ResultComponentDiff:
            print('\t NodePair: init: {:<5} updated: {:<5}'.format(item.RootNode_init.id, item.RootNode_updated.id))
            print('\t  Recursion steps: {}'.format(item.recursionCounter ))
            print('\t  Time: {}'.format(item.time))
            print('\t  RATIO Time vs. Recursion steps: {:7.4f}'.format(item.time / item.recursionCounter ))

            if item.isSimilar:
                print('\t  Unchanged: TRUE')
            else: 
                print('\t  Unchanged: FALSE')

            if not item.isSimilar:
                for res in item.propertyModifications:
                    print('\t   PropertyMod: NodeId_INIT: {:<5} NodeId_UPDATED: {:<5}'.format(res.nodeId_init, res.nodeId_updated))
                    print('\t    |-> ModificationType: {:<15} attrName: {:<12} oldValue: {:<10} newValue: {:<10}'.format(res.modificationType, res.attrName, res.valueOld, res.valueNew))
                
                for res in item.StructureModifications:
                    print('\t   StructuralMod: NodeId_PARENT: {:<5} NodeId_Child: {:<5}'.format(res.parentId, res.childId))
                    print('\t    |-> ModificationType: {:<15} '.format(res.modType))
            print()

    def printTimeFigures(self): 

        pairs          = np.arange( 1, len(self.ResultComponentDiff) + 1 )
        times_vec      = np.array( [o.time for o in self.ResultComponentDiff] )
        recursionSteps = np.array([o.recursionCounter for o in self.ResultComponentDiff])

        ratios = np.divide(times_vec, recursionSteps)

        plt.subplot(3, 1, 1)
        plt.plot(pairs, times_vec, '-')
        plt.grid(True)
        plt.xlabel('component Tuple')
        plt.ylabel('time [s]')
        plt.title('Elapsed Time')

        plt.subplot(3, 1, 2)

        plt.plot(pairs, recursionSteps, '-')

        plt.xlabel('component Tuple')
        plt.ylabel('recursion steps')
        plt.title('Recursion steps')
        plt.grid(True)

        plt.subplot(3, 1, 3)
        
        plt.plot(pairs, ratios, '-', lw=2)

        plt.title('Ratio')

        plt.xlabel('component Tuple')
        plt.ylabel('ratio [steps/time] ')
        plt.grid(True)

        plt.tight_layout()
        plt.show()


    def __str__(self):
        """ dunder method to pretty print the Reporter object object to console. If results are intented, use print(inst.result)""" 
        pass


    def reportToJSON(self):
        """ formats the result object into a nice json object and returns the json string """
        pass 





