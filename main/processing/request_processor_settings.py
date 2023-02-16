from abc import abstractmethod


class RequestProcessorSettings:
    @abstractmethod
    def get_expected_input_keys(self) -> list:
        pass

    @abstractmethod
    def get_required_parameters(self) -> list:
        pass

    @abstractmethod
    def get_bikeCad_to_model_map(self) -> dict:
        pass

    @abstractmethod
    def keys_whose_presence_indicates_their_value(self) -> list:
        pass

    @abstractmethod
    def millimeters_to_meters(self) -> list:
        pass
