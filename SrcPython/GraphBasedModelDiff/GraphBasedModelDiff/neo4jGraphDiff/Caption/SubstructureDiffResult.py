""" packages """
from enum import Enum

from neo4jGraphDiff.AbsResult import Result
from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class SubstructureDiffResult(Result):
    """carries the diff result """

    def __init__(self, root_init: NodeItem, root_updated: NodeItem, method=None):
        super().__init__()
        self.isSimilar: bool = True
        self.method = method
        self.propertyModifications:list(PropertyModification) = []
        self.StructureModifications: list(StructureModification) = []
        self.time: float = 0.0
        self.RootNode_init: NodeItem = root_init
        self.RootNode_updated: NodeItem = root_updated
        self.recursionCounter = 0

    def logNodeModification(self, nodeId_init, nodeId_updated, attrName, modType, value_old, value_new, graph_path_init, graph_path_updated):
        """ logs a modification applied on properties """
        modification = PropertyModification(nodeId_init, nodeId_updated, attrName, modType, value_old, value_new)

        # set exact graph path
        modification.set_paths(graph_path_init, graph_path_updated)

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


class PropertyModification:

    def __init__(self, id_init, id_updated, attrName, modificationType, value_old=None, value_new=None):
        self.nodeId_init = id_init
        self.nodeId_updated = id_updated
        self.attrName = attrName
        self.valueOld = value_old
        self.valueNew = value_new
        sw = {"added": PropertyModificationTypeEnum.ADDED,
              "deleted": PropertyModificationTypeEnum.DELETED,
              "modified": PropertyModificationTypeEnum.MODIFIED}
        self.modificationType = sw[modificationType]
        self.path_init: str
        self.path_updated: str

    def set_paths(self, path_init, path_updated):
        self.path_init = path_init
        self.path_updated = path_updated

    def __repr__(self):
        return 'PMod: node_init: {} node_updated: {} attr: {} action: {} oldVal: {} newVal: {}'.format(self.nodeId_init,
                                                                                                       self.nodeId_updated,
                                                                                                       self.attrName,
                                                                                                       self.modificationType,
                                                                                                       self.valueOld,
                                                                                                       self.valueNew)


class PropertyModificationTypeEnum(Enum):
    ADDED = 1
    DELETED = 2
    MODIFIED = 3


class StructureModification:

    def __init__(self, parentId, childId, modificationType):
        self.parentId = parentId
        self.childId = childId
        sw = {"added": StructuralModificationTypeEnum.ADDED,
              "deleted": StructuralModificationTypeEnum.DELETED}
        self.modType = sw[modificationType]

    def __repr__(self):
        return 'Structure Modification: parentId: {} childId: {} action: {}'.format(self.parentId, self.childId,
                                                                                    self.modType)


class StructuralModificationTypeEnum(Enum):
    ADDED = 1
    DELETED = 2