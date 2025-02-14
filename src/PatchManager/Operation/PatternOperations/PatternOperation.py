import abc

from PatchManager.Operation.AbstractOperation import AbstractOperation
from neo4j_middleware.ResponseParser.GraphPattern import GraphPattern


class PatternOperation(AbstractOperation):
    """
    Abstract class of all pattern operations
    """
    pattern: GraphPattern
    reference_structure: GraphPattern

    @abc.abstractmethod
    def __init__(self):
        super().__init__()


