from typing import List

from neo4jGraphDiff.Caption.NodeMatchingTable import NodeMatchingTable
from neo4jGraphDiff.Caption.PropertyModification import PropertyModification
from neo4jGraphDiff.Caption.StructureModification import StructureModification
from neo4jGraphDiff.Caption.SubstructureDiffResult import SubstructureDiffResult


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

    def calculate_added_nodes(self):
        """
        method to calculate all nodes that were added. Calculation is based on the SIMILAR_TO relationship work
        @return:
        """

    def sort_pMods_by_guid(self):
        lst = sorted(self.property_updates, key=lambda pmod: pmod.pattern.get_entry_node().attrs['GlobalId'])
        return lst
