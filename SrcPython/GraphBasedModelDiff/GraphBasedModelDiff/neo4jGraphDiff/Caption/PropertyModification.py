from enum import Enum

from neo4j_middleware.ResponseParser.GraphPath import GraphPath


class PropertyModification:

    def __init__(self, id_init, id_updated, attrName, modificationType, value_old = None, value_new = None):
        self.nodeId_init = id_init
        self.nodeId_updated = id_updated
        self.attrName = attrName
        self.valueOld = value_old
        self.valueNew = value_new
        sw = {"added": PropertyModificationTypeEnum.ADDED,
              "deleted": PropertyModificationTypeEnum.DELETED,
              "modified": PropertyModificationTypeEnum.MODIFIED}
        self.modificationType = sw[modificationType]
        self.path_init: GraphPath
        self.path_updated: GraphPath

    def set_paths(self, path_init, path_updated):
        self.path_init = path_init
        self.path_updated = path_updated

    def __repr__(self):
        return 'PMod: node_init: {} node_updated: {} attr: {} action: {} oldVal: {} newVal: {}' \
            .format(self.nodeId_init,
                    self.nodeId_updated,
                    self.attrName,
                    self.modificationType,
                    self.valueOld,
                    self.valueNew)


class PropertyModificationTypeEnum(Enum):
    ADDED = 1
    DELETED = 2
    MODIFIED = 3
