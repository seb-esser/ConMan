from typing import List

from neo4jGraphDiff.Caption.NodeMatchingTable import NodeMatchingTable
from neo4jGraphDiff.Caption.PropertyModification import PropertyModification
from neo4jGraphDiff.Caption.StructureModification import StructureModification, StructuralModificationTypeEnum
from neo4jGraphDiff.Caption.SubstructureDiffResult import SubstructureDiffResult
from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class Result:

    def __init__(self, label_init: str, label_updated: str):
        """
        global capture of graph mutations

        @param label_init:
        @param label_updated:
        """
        self.ts_init = label_init
        self.ts_updated = label_updated

        self.node_matching_table: NodeMatchingTable = NodeMatchingTable()

        self.property_updates: List[PropertyModification] = []
        self.structure_updates: List[StructureModification] = []

    def append_sub_result(self, sub_res: SubstructureDiffResult):

        if len(sub_res.propertyModifications) > 0:
            self.property_updates += sub_res.propertyModifications

        if len(sub_res.StructureModifications) > 0:
            self.structure_updates += sub_res.StructureModifications

        # store matched nodes
        self.node_matching_table.append_pairs(sub_res.nodeMatchingTable)

    def sort_pMods_by_guid(self):
        lst = sorted(self.property_updates, key=lambda pmod: pmod.pattern.get_entry_node().attrs['GlobalId'])
        return lst

    def unify_pMods(self):
        """
        removes duplicates from pMod list
        """
        sorted = []
        for pmod in self.property_updates:
            if pmod not in sorted:
                sorted.append(pmod)

        self.property_updates = sorted
        return sorted

    def get_node_list_inserted(self):
        """
        returns a list of nodeItems that are already captured as inserted
        """

        lst: List[NodeItem] = []

        for smod in self.structure_updates:
            if smod.child not in lst and smod.modType == StructuralModificationTypeEnum.ADDED:
                lst.append(smod.child)
        return lst

    def get_node_list_removed(self):
        """
        returns a list of nodeItems that are already captured as removed
        """

        lst: List[NodeItem] = []

        for smod in self.structure_updates:
            if smod.child not in lst and smod.modType == StructuralModificationTypeEnum.DELETED:
                lst.append(smod.child)
        return lst
