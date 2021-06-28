from PatchManager.Operation.AttributeOperations.AttributeOperation import AttributeOperation


class ModifyAttributeOperation(AttributeOperation):

    def __init__(self, prim_guid: str, pattern: str, attrName: str, attrValOld, attrValNew):
        """

        @param prim_guid:
        @param pattern:
        @param attrName:
        @param attrValOld:
        @param attrValNew:
        """
        self.initial_value = attrValOld
        self.updated_value = attrValNew
        super().__init__(prim_guid=prim_guid, pattern=pattern, attrName=attrName)


