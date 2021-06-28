import json

from PatchManager.Operation.AbstractOperation import AbstractOperation


class AttributeOperation(AbstractOperation):

    def __init__(self, prim_guid: str, pattern: str, attrName: str):
        """

        @param prim_guid:
        @param pattern:
        @param attrName:
        """
        self.primary_node_guid: str = prim_guid
        self.node_pattern: str = pattern
        self.attribute_name: str = attrName


    def to_json(self):
        return json.dump(self)
