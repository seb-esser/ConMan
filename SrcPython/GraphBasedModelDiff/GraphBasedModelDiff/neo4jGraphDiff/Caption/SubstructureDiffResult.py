""" packages """
from enum import Enum

from typing import List

from neo4jGraphDiff.AbsResult import Result
from neo4jGraphDiff.Caption.PropertyModification import PropertyModification
from neo4jGraphDiff.Caption.StructureModification import StructureModification
from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class SubstructureDiffResult(Result):
    """carries the diff result """

    def __init__(self, root_init: NodeItem, root_updated: NodeItem, method=None):
        super().__init__()
        self.isSimilar: bool = True
        self.method = method
        self.propertyModifications: List[PropertyModification] = []
        self.StructureModifications: List[StructureModification] = []
        self.time: float = 0.0
        self.RootNode_init: NodeItem = root_init
        self.RootNode_updated: NodeItem = root_updated
        self.recursionCounter = 0

    def logNodeModification(self,
                            nodeId_init: int,
                            nodeId_updated: int,
                            attrName: str,
                            modType: str,
                            value_old,
                            value_new,
                            graphPattern):
        """
        captures a property modification on node attributes
        @param graphPattern:
        @param nodeId_init:
        @param nodeId_updated:
        @param attrName:
        @param modType:
        @param value_old:
        @param value_new:

        @return:
        """
        modification = PropertyModification(nodeId_init, nodeId_updated, attrName, modType, graphPattern, value_old, value_new)

        self.propertyModifications.append(modification)
        self.isSimilar = False

    def logStructureModification(self, parentNodeId, childNodeId, modType):
        """ logs a new modification to the SubstructureDiffResult.modifiedNodes container """
        modification = StructureModification(parentNodeId, childNodeId, modType)
        self.StructureModifications.append(modification)
        self.isSimilar = False

    def setComputeTime(self, time):
        self.time = time

    def increaseRecursionCounter(self):
        self.recursionCounter += 1




