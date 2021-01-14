
""" packages """
from enum import Enum

""" modules """
from neo4jGraphDiff.Result import Result

class DiffResult(Result):
    """carries the diff result """

    def __init__(self, method = None):
        self.isSimilar = True
        self.method = method
        self.propertyModifications = []
        self.StructureModifications = []

    def logNodeModification(self, nodeId, attrName, modType, value_old, value_new):
        """ logs a modification applied on properties """
        modification = PropertyModification(nodeId, attrName, modType, value_old, value_new)
        self.propertyModifications.append(modification)

    def logStructureModification(self, parentNodeId, childNodeId, modType):
        """ logs a new modification to the DiffResult.modifiedNodes container """
        modification = StructureModification(parentNodeId, childNodeId, modType)
        self.propertyModifications.append(modification)

class PropertyModification: 

    def __init__(self, id, attrName, modType, value_old = None, value_new = None ):
        self.nodeId = id
        self.attrName = attrName
        self.valueOld = value_old
        self.valueNew = value_new
        sw = {"added":      PropertyModificationTypeEnum.ADDED, 
              "deleted":    PropertyModificationTypeEnum.DELETED, 
              "modified":   PropertyModificationTypeEnum.MODIFIED}
        self.modificationType = sw[modificationType]

    def __repr__(self):
        return 'Property Modification: node: {} attr: {} action: {}'.format(self.nodeId, self.attrName, self.modType)

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
        return 'Structure Modification: parentId: {} childId: {} action: {}'.format(self.parentId, self.childId, self.modType)

class StructuralModificationTypeEnum(Enum): 
    ADDED = 1
    DELETED = 2


