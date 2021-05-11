from abc import ABC, abstractmethod


class BaseUpdater(ABC):
    @abstractmethod
    def update(self):
        pass
