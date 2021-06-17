from GraphBasedModelDiff.PatchManager.Operation.NodeOperations.NodeOperation import NodeOperation


class AddNodeOperation(NodeOperation):

    def __init__(self):
        self.parent_node_path = None
        self.node_label: str
        self.node_attributes: dict

