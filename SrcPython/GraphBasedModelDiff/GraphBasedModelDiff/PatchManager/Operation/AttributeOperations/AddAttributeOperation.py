from PatchManager.Operation.AttributeOperations.AttributeOperation import AttributeOperation


class AddAttributeOperation(AttributeOperation):

    def __init__(self, prim_guid: str, pattern: str, attrName: str, attrValNew):
        """

        @param prim_guid:
        @param pattern:
        @param attrName:
        @param attrValNew:
        """
        self.updated_value = attrValNew
        super().__init__(prim_guid=prim_guid, pattern=pattern, attrName=attrName)

