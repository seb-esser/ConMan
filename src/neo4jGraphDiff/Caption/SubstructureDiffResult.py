""" packages """
from enum import Enum

from typing import List

from neo4jGraphDiff.Caption.NodeMatchingTable import NodeMatchingTable
from neo4jGraphDiff.Caption.PropertyModification import PropertyModification
from neo4jGraphDiff.Caption.StructureModification import StructureModification
from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class SubstructureDiffResult:
    """carries the diff result """

    def __init__(self, root_init: NodeItem = None, root_updated: NodeItem = None, method = None):
        super().__init__()
        self.isSimilar: bool = True
        self.method = method
        self.propertyModifications: List[PropertyModification] = []
        self.StructureModifications: List[StructureModification] = []
        self.time: float = 0.0
        self.RootNode_init: NodeItem = root_init
        self.RootNode_updated: NodeItem = root_updated
        self.recursionCounter = 0

        self.nodeMatchingTable: NodeMatchingTable = NodeMatchingTable()

    def logNodeModification(self,
                            node_init: NodeItem,
                            node_updated: NodeItem,
                            attrName: str,
                            modType: str,
                            value_old,
                            value_new,
                            graphPattern):
        """
        captures a property modification on node attributes
        @param graphPattern:
        @param node_init:
        @param node_updated:
        @param attrName:
        @param modType:
        @param value_old:
        @param value_new:

        @return:
        """
        modification = PropertyModification(node_init, node_updated, attrName, modType, graphPattern, value_old,
                                            value_new)

        self.propertyModifications.append(modification)
        self.isSimilar = False

    def logStructureModification(self, parentNode: NodeItem, childNode: NodeItem, modType):
        """
        captures a structural modification in the graph
        @param parentNode:
        @param childNode:
        @param modType:
        @return:
        """
        modification = StructureModification(parentNode, childNode, modType)
        self.StructureModifications.append(modification)
        self.isSimilar = False

    def setComputeTime(self, time):
        self.time = time

    def increaseRecursionCounter(self):
        self.recursionCounter += 1

    def set_nodes(self, node_init, node_updated):
        self.RootNode_init = node_init
        self.RootNode_updated = node_updated
