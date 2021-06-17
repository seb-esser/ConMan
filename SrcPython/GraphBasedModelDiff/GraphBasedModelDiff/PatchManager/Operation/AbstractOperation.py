import abc


class AbstractOperation(abc.ABC):
    """
    abstract base class for all patch operations
    """
    @abc.abstractmethod
    def __init__(self):
        pass
