from abc import abstractmethod, ABCMeta


class RequestProcessorSettings(metaclass=ABCMeta):

    @abstractmethod
    def expected_xml_keys(self) -> list:
        pass

    @abstractmethod
    def expected_input_keys(self) -> list:
        pass

    @abstractmethod
    def required_parameters(self) -> list:
        pass

    @abstractmethod
    def bikeCad_to_model_map(self) -> dict:
        pass

    @abstractmethod
    def label_replacements(self) -> dict:
        pass

    @abstractmethod
    def keys_whose_presence_indicates_their_value(self) -> list:
        pass

    @abstractmethod
    def millimeters_to_meters(self) -> list:
        pass
