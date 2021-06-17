import abc

from PatchManager.Operation.AbstractOperation import AbstractOperation


class NodeOperation(AbstractOperation):

    @abc.abstractmethod
    def __init__(self):
        super().__init__()
