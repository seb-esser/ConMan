""" package import """
import matplotlib.pyplot as plt
import numpy as np

""" module import """
from neo4jGraphDiff.Caption.SubstructureDiffResult import SubstructureDiffResult

""" class def """


class ResultGenerator:
    """description of class"""

    def __init__(self, usedConfig=None):
        """ """
        self.config = usedConfig

        self.ResultRooted = {}
        self.ResultComponentDiff = []

    def capture_result_primary(self, rootDiffRes: list):
        """
        Captures the comparison result of rooted nodes
        @param rootDiffRes: list of 3 items representing unchanged, added and deleted nodes
        """
        nodes_unchanged = rootDiffRes[0]
        nodes_added = rootDiffRes[1]
        nodes_deleted = rootDiffRes[2]

        self.ResultRooted['unchanged'] = nodes_unchanged
        self.ResultRooted['added'] = nodes_added
        self.ResultRooted['deleted'] = nodes_deleted

    def capture_result_con_nodes(self):
        """ captures SubstructureDiffResult of ObjRel structure Diff """
        pass

    def capture_result_secondary(self, diffRes: SubstructureDiffResult):
        """
        captures SubstructureDiffResult of a componentDiff
        @param diffRes:
        """
        self.ResultComponentDiff.append(diffRes)

    def print_report(self):
        """
        prints the reporter content to console in a formatted way
        """
        print('\n')
        print('--- --- --- --- --- --- --- --  --- --- --- --- --- --- ')
        print('--- --- --- --- --- --- REPORT  --- --- --- --- --- --- \n')
        print('--- --- --- --- --- --- --- --  --- --- --- --- --- --- ')

        print('Applied Config: ')
        print(self.config)
        print(self.config.DiffSettings)

        print('\n _______ PRIMARY STRUCTURE ______________')

        print('\nROOT NODES:')

        print('\t NODES-PAIRS UNCHANGED: ')
        for item in self.ResultRooted['unchanged']:
            print \
                ('\t  init: NodeId:{:<5} EntityType: {:<26} updated: NodeId:{:<5} EntityType: {:<26}'.format(item[0].id,
                                                                                                             item
                                                                                                             [
                                                                                                                 0].entityType,
                                                                                                             item[1].id,
                                                                                                             item
                                                                                                             [
                                                                                                                 1].entityType))

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

        print('\nCONNECTION NODE STRUCTURE:')
        print()

        print('\n _______ SECONDARY STRUCTURES ____________')

        for item in self.ResultComponentDiff:
            print('\t NodePair: init: {:<5} updated: {:<5}'.format(item.RootNode_init.id, item.RootNode_updated.id))
            print('\t  Recursion steps: {}'.format(item.recursionCounter))
            print('\t  Time: {}'.format(item.time))
            print('\t  RATIO Time vs. Recursion steps: {:7.4f}'.format(item.time / item.recursionCounter))

            if item.isSimilar:
                print('\t  Unchanged: TRUE')
            else:
                print('\t  Unchanged: FALSE')

            if not item.isSimilar:
                for res in item.propertyModifications:
                    print('\t   PropertyMod: NodeId_INIT: {:<5} NodeId_UPDATED: {:<5}'.format(res.nodeId_init,
                                                                                              res.nodeId_updated))
                    print \
                        ('\t    |-> ModificationType: {:<15} attrName: {:<12} oldValue: {:<20} newValue: {:<20}'.format
                         (res.modificationType, res.attrName, res.valueOld, res.valueNew))

                for res in item.StructureModifications:
                    print('\t   StructuralMod: NodeId_PARENT: {:<5} NodeId_Child: {:<5}'.format(res.parentId,
                                                                                                res.childId))
                    print('\t    |-> ModificationType: {:<15} '.format(res.modType))
            print()

    def print_time_plot(self):
        """
        creates a pyplot showing the consumed times
        """
        pairs = np.arange(1, len(self.ResultComponentDiff) + 1)
        times_vec = np.array([o.time for o in self.ResultComponentDiff])
        recursionSteps = np.array([o.recursionCounter for o in self.ResultComponentDiff])

        ratios = np.divide(times_vec, recursionSteps)

        plt.subplot(3, 1, 1)
        plt.plot(pairs, times_vec, 'o-', color='blue', markerfacecolor='lightgrey')
        plt.grid(True)
        plt.xlabel('component Tuple')
        plt.ylabel('time [s]')
        plt.title('Elapsed Time')

        plt.subplot(3, 1, 2)

        plt.plot(pairs, recursionSteps, 'o-', color='blue', markerfacecolor='lightgrey')

        plt.xlabel('component Tuple')
        plt.ylabel('recursion steps')
        plt.title('Recursion steps')
        plt.grid(True)

        plt.subplot(3, 1, 3)

        plt.plot(pairs, ratios, 'o-', color='blue', markerfacecolor='lightgrey')

        plt.title('Ratio')

        plt.xlabel('component Tuple')
        plt.ylabel('ratio [steps/time] ')
        plt.grid(True)

        plt.tight_layout()
        plt.show()

    def __str__(self):
        pass
