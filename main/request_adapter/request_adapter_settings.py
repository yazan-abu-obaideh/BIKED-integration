from abc import abstractmethod


class RequestAdapterSettings:
    @abstractmethod
    def default_values(self) -> dict:
        pass

    @abstractmethod
    def bikeCad_to_model_map(self) -> dict:
        pass

    @abstractmethod
    def keys_whose_presence_indicates_their_value(self) -> list:
        pass

    @abstractmethod
    def raise_exception_if_missing(self) -> list:
        pass
