from GraphBasedModelDiff.neo4jGraphDiff.Operation.AttributeOperations.AttributeOperation import AttributeOperation


class AddAttributeOperation(AttributeOperation):

    def __init__(self):
        self.node_path : str
        self.attribute_name: str
        self.attribute_value: object

