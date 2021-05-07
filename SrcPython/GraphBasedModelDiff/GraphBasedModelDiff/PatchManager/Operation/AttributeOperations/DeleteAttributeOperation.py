from PatchManager.Operation.AttributeOperations.AttributeOperation import AttributeOperation


class DeleteAttributeOperation(AttributeOperation):

    def __init__(self, prim_hash: str, pattern: str, attrName: str, attrValOld):
        self.initial_value = attrValOld
        super().__init__(prim_hash=prim_hash, pattern=pattern, attrName=attrName)
