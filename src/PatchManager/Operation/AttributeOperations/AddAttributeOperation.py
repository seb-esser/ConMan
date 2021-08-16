from PatchManager.Operation.AttributeOperations.AttributeOperation import AttributeOperation
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern


class AddAttributeOperation(AttributeOperation):

    def __init__(self, prim_guid: str, pattern: GraphPattern, attrName: str, attrValNew):
        """

        @param prim_guid:
        @param pattern:
        @param attrName:
        @param attrValNew:
        """
        self.updated_value = attrValNew
        super().__init__(prim_guid=prim_guid, pattern=pattern, attrName=attrName)

