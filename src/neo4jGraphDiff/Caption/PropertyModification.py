from enum import Enum

from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern
from neo4j_middleware.ResponseParser.NodeItem import NodeItem


class PropertyModification:

    def __init__(self, init: NodeItem, updated: NodeItem, attrName: str, modificationType, pattern: GraphPattern, value_old = None, value_new = None):
        self.pattern = pattern
        self.node_init: NodeItem = init
        self.node_updated: NodeItem = updated
        self.attrName = attrName
        self.valueOld = value_old
        self.valueNew = value_new
        sw = {"added": PropertyModificationTypeEnum.ADDED,
              "deleted": PropertyModificationTypeEnum.DELETED,
              "modified": PropertyModificationTypeEnum.MODIFIED}
        self.modificationType = sw[modificationType]

    def __repr__(self):
        return 'PMod: node_init: {} node_updated: {} attr: {} action: {} oldVal: {} newVal: {}' \
            .format(self.node_init.id,
                    self.node_updated.id,
                    self.attrName,
                    self.modificationType,
                    self.valueOld,
                    self.valueNew)


class PropertyModificationTypeEnum(Enum):
    ADDED = 1
    DELETED = 2
    MODIFIED = 3
