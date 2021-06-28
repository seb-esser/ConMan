from PatchManager.Operation.AttributeOperations.AttributeOperation import AttributeOperation


class DeleteAttributeOperation(AttributeOperation):

    def __init__(self, prim_guid: str, pattern: str, attrName: str, attrValOld):
        """

        @param prim_guid:
        @param pattern:
        @param attrName:
        @param attrValOld:
        """
        self.initial_value = attrValOld
        super().__init__(prim_guid=prim_guid, pattern=pattern, attrName=attrName)
