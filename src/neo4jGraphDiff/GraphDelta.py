from typing import List

from neo4jGraphDiff.Caption.NodeMatchingTable import NodeMatchingTable
from neo4jGraphDiff.Caption.PropertyModification import PropertyModification
from neo4jGraphDiff.Caption.StructureModification import StructureModification, StructuralModificationTypeEnum
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class GraphDelta:

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

    def sort_pMods_by_guid(self):
        """
        sorts the pMods by the globalId attribute
        @return:
        """
        try:
            lst = sorted(self.property_updates, key=lambda pmod: pmod.pattern.get_entry_node().attrs['GlobalId'])
            return lst
        except:
            print('Sorting failed. Perhaps there is an issue in a pattern for each pMod. ')
            return self.property_updates

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

    def capture_structure_mod(self, parent_node: NodeItem, child_node: NodeItem, modType):
        """
        appends a structural modification to the delta
        """
        modification = StructureModification(parent_node, child_node, modType)
        self.structure_updates.append(modification)

    def capture_property_mod(self, node_init: NodeItem, node_updated: NodeItem,
                             attr_name: str, mod_type: str, value_old, value_new, graph_pattern: GraphPattern):
        """
        appends a property modification to the delta
        """
        modification = PropertyModification(node_init, node_updated, attr_name, mod_type, graph_pattern, value_old,
                                            value_new)

        self.property_updates.append(modification)

    def capture_property_mod_instance(self, pm: PropertyModification):
        """
        adds an instance of a propertyModification
        @param pm:
        @return:
        """
        self.property_updates.append(pm)
