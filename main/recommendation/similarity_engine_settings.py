from abc import abstractmethod, ABCMeta


class EngineSettings(metaclass=ABCMeta):

    @abstractmethod
    def include(self) -> list:
        pass

    @abstractmethod
    def max_n(self) -> int:
        pass

    @abstractmethod
    def weights(self) -> dict:
        pass
