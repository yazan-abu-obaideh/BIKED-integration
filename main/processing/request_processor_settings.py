from abc import abstractmethod


class RequestProcessorSettings:
    @abstractmethod
    def expected_input_keys(self) -> list:
        pass

    @abstractmethod
    def raise_exception_if_missing(self) -> list:
        pass

    @abstractmethod
    def bikeCad_to_model_map(self) -> dict:
        pass

    @abstractmethod
    def keys_whose_presence_indicates_their_value(self) -> list:
        pass

    @abstractmethod
    def millimeters_to_meters(self) -> list:
        pass
