from PatchManager.Operation.PatternOperations.PatternOperation import PatternOperation


class AddPatternOperation(PatternOperation):

    def __init__(self, pattern):
        """

        @param pattern:
        @return:
        """
        self.pattern = pattern

    def __repr__(self):
        return 'AddPatternOp: {}'.format(self.pattern)

