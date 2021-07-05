import json

from PatchManager.Operation.AbstractOperation import AbstractOperation
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern


class AttributeOperation(AbstractOperation):

    def __init__(self, prim_guid: str, pattern: GraphPattern, attrName: str):
        """

        @param prim_guid:
        @param pattern:
        @param attrName:
        """
        self.primary_node_guid: str = prim_guid
        self.node_pattern: GraphPattern = pattern
        self.attribute_name: str = attrName

    def to_json(self):
        return json.dump(self)
