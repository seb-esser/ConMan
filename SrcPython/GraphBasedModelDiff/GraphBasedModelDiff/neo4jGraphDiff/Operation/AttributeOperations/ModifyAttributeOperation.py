from GraphBasedModelDiff.neo4jGraphDiff.Operation.AttributeOperations.AttributeOperation import AttributeOperation


class ModifyAttributeOperation(AttributeOperation):

    def __init__(self):
        self.new_attribute_value: object

