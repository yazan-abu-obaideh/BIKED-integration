from main.xml_handler import XmlHandler
from main.request_adapter.request_adapter_settings import RequestAdapterSettings


class RequestAdapter:
    def __init__(self, settings: RequestAdapterSettings):
        self.xml_handler = XmlHandler()
        self.settings = settings

    def convert_xml(self, raw_xml: str) -> dict:
        self.set_xml_or_throw(raw_xml)
        bikeCad_file_entries = self.xml_handler.get_entries_dict()
        return self.convert_dict(bikeCad_file_entries)

    def set_xml_or_throw(self, raw_xml):
        try:
            self.xml_handler.set_xml(raw_xml)
        except ValueError:
            raise ValueError("Invalid BikeCAD file")

    def convert_dict(self, bikeCad_file_entries):
        result_dict = self.map_to_model_input(bikeCad_file_entries)
        result_dict = self.parse_values(result_dict)
        self.convert_units(result_dict)
        self.handle_special_behavior(bikeCad_file_entries, result_dict)
        self.fill_default(result_dict)
        return result_dict

    def map_to_model_input(self, bikeCad_file_entries):
        result_dict = {}
        for key, value in bikeCad_file_entries.items():
            model_key = self.settings.bikeCad_to_model_map().get(key, key)
            if self.valid_model_key(model_key):
                result_dict[model_key] = value
        return result_dict

    def valid_model_key(self, model_key):
        return model_key in self.settings.default_values().keys()

    def handle_special_behavior(self, bikeCad_file_entries, result_dict):
        self.one_hot_encode(result_dict, bikeCad_file_entries["MATERIAL"])
        self.handle_keys_whose_presence_indicates_their_value(result_dict)
        self.handle_ramifications(result_dict)

    def one_hot_encode(self, result_dict, materials_entry: str):
        result_dict[f"Material={materials_entry.lower().title()}"] = 1

    def handle_keys_whose_presence_indicates_their_value(self, result_dict):
        for key in self.settings.keys_whose_presence_indicates_their_value():
            # TODO: ask Lyle whether it's a bug or a feature that CSB_Include is
            #  assigned to 0 in both the IF and ELSE clauses
            result_dict[key] = int(key in result_dict)

    def handle_ramifications(self, result_dict):
        # TODO: check whether this should be done before or after scaling
        if result_dict["CSB_Include"] == 0:
            result_dict["CSB OD"] = 0.017759
        if result_dict["SSB_Include"] == 0:
            result_dict["SSB OD"] = 0.015849

    def fill_default(self, result_dict):
        for key, value in self.settings.default_values().items():
            if key not in result_dict:
                result_dict[key] = value

    def parse_values(self, result_dict):
        return {key: self.get_float_or_strip(value) for key, value in result_dict.items()}

    def get_float_or_strip(self, value):
        try:
            return float(value)
        except ValueError:
            return str(value).strip()

    def convert_units(self, result_dict):
        for key, divider in self.settings.unit_conversion_division_dict().items():
            result_dict[key] = result_dict[key]/divider
