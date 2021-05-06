import json

from PatchManager.Operation.AbstractOperation import AbstractOperation


class AttributeOperation(AbstractOperation):

    def __init__(self, prim_hash: str, pattern: str, attrName: str):
        self.primary_node_hash: str = prim_hash
        self.node_pattern: str = pattern
        self.attribute_name: str = attrName


    def to_json(self):
        return json.dump(self)
