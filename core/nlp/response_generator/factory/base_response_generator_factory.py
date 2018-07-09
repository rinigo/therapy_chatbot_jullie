from abc import ABC, abstractmethod


class BaseResponseGeneratorFactory(ABC):
    @classmethod
    @abstractmethod
    def create(cls, *arguments):
        pass
