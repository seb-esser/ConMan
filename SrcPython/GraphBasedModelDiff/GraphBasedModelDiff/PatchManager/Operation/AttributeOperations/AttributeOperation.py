from GraphBasedModelDiff.PatchManager.Operation.AbstractOperation import AbstractOperation


class AttributeOperation(AbstractOperation):

    def __init__(self):
        self.node_path: str
        self.attribute_name: str
