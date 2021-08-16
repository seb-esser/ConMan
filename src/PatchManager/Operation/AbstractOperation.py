import abc


class AbstractOperation(abc.ABC):
    """
    abstract base class for all patch operations
    """

    primary_node_guid: str

    @abc.abstractmethod
    def __init__(self):
        pass
