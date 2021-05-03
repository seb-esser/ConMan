from GraphBasedModelDiff.neo4jGraphDiff.Operation.NodeOperations.NodeOperation import NodeOperation


class DeleteNodeOperation(NodeOperation):

    def __init__(self):
        delete_substructure: bool = False  # set to True if subtree should be deleted as well
