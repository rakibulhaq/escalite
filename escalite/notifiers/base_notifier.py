import abc
from abc import ABC


class BaseNotifier(ABC):
    @abc.abstractmethod
    def notify(self, message: str, data: dict ):
        pass

    @abc.abstractmethod
    def set_config(self, config: dict):
        pass
