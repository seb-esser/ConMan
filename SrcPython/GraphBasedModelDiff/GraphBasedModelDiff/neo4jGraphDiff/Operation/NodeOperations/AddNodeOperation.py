from GraphBasedModelDiff.neo4jGraphDiff.Operation.NodeOperations.NodeOperation import NodeOperation


class AddNodeOperation(NodeOperation):

    def __init__(self):
        self.parent_node_path = None
        self.node_label: str = None
        self.node_attributes: dict = None

