from abc import abstractmethod, ABCMeta
from typing import Tuple


class RequestProcessorSettings(metaclass=ABCMeta):

    @abstractmethod
    def butted_wall_map(self) -> dict:
        pass

    @abstractmethod
    def is_butted_template(self, key) -> str:
        pass

    @abstractmethod
    def wall_pair_templates(self, key) -> Tuple[str, str]:
        pass

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
    def keys_whose_presence_indicates_their_value(self) -> list:
        pass

    @abstractmethod
    def millimeters_to_meters(self) -> list:
        pass
