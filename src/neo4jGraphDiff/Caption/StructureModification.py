from enum import Enum

from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class StructureModification:

    def __init__(self, parent: NodeItem, child: NodeItem, modificationType):
        self.parent: NodeItem = parent
        self.child: NodeItem = child
        sw = {"added": StructuralModificationTypeEnum.ADDED,
              "deleted": StructuralModificationTypeEnum.DELETED}
        self.modType = sw[modificationType]

    def __repr__(self):
        return 'Structure Modification: parentId: {} childId: {} action: {}'.format(self.parent.id, self.child.id,
                                                                                    self.modType)


class StructuralModificationTypeEnum(Enum):
    ADDED = 1
    DELETED = 2
