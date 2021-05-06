from PatchManager.Operation.AttributeOperations.AttributeOperation import AttributeOperation


class AddAttributeOperation(AttributeOperation):

    def __init__(self, prim_hash: str, pattern: str, attrName: str, attrValNew):
        self.updated_value = attrValNew
        super().__init__(prim_hash=prim_hash, pattern=pattern, attrName=attrName)

