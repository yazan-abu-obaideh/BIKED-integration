from abc import abstractmethod, ABCMeta


class FramedMapperSettings(metaclass=ABCMeta):

    @abstractmethod
    def get_expected_xml_keys(self):
        pass

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
    def get_label_replacements(self):
        pass

    @abstractmethod
    def keys_whose_presence_indicates_their_value(self) -> list:
        pass

    @abstractmethod
    def millimeters_to_meters(self) -> list:
        pass
