from PatchManager.Operation.PatternOperations.PatternOperation import PatternOperation
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern


class RemovePatternOperation(PatternOperation):

    def __init__(self, pattern):
        """

        @param pattern:
        @return:
        """
        super().__init__()
        self.pattern = pattern

    def __repr__(self):
        return 'RemovePatternOp: {}'.format(self.pattern)

