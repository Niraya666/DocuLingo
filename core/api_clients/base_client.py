from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    @abstractmethod
    def vision_request(self, messages, **kwargs):
        pass

    @abstractmethod
    def text_request(self, messages, **kwargs):
        pass