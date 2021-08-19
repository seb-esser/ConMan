from PatchManager.Operation.PatternOperations.PatternOperation import PatternOperation
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern


class RemovePatternOperation(PatternOperation):

    def __init__(self, pattern: GraphPattern, reference_structure: GraphPattern, prim_guid: str):
        """

        @param pattern:
        @return:
        """
        super().__init__()
        self.primary_node_guid = prim_guid
        self.pattern = pattern
        self.reference_structure = reference_structure

    def __repr__(self):
        return 'RemovePatternOp: {}'.format(self.pattern)

