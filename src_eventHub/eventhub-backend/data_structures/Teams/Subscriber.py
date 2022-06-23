import abc
from abc import ABC


class Subscriber(abc.ABC):

    @abc.abstractmethod
    def __init__(self):
        pass
