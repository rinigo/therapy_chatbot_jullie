from abc import ABC, abstractmethod


class BaseBot(ABC):
    @abstractmethod
    def reply(self, *arguments):
        pass

    @abstractmethod
    def create_response(self, *arguments):
        pass

    @abstractmethod
    def send_responses(self, *arguments):
        pass
