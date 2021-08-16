from enum import Enum


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
