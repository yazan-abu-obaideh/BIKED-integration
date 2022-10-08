from production.xml_handler import XmlHandler
from production.request_adapter.settings import default_values, \
    keys_whose_presence_indicates_their_value, bikeCad_to_model_map

DEFAULT_VALUE = 0


class RequestAdapter:
    def __init__(self):
        self.xml_handler = XmlHandler()
        # noinspection SpellCheckingInspection
        self.bikeCad_to_model_map = bikeCad_to_model_map
        self.default_values = default_values

    def convert(self, raw_xml: str) -> dict:
        self.xml_handler.set_xml(raw_xml)

        bikeCad_file_entries = self.xml_handler.get_entries_dict()

        result_dict = self.transform_to_model(bikeCad_file_entries)
        self.handle_special_behavior(bikeCad_file_entries, result_dict)
        self.handle_ramifications(result_dict)
        self.fill_default(result_dict)

        return result_dict

    def transform_to_model(self, bikeCad_file_entries):
        result_dict = {}
        for key, value in bikeCad_file_entries.items():
            model_key = self.bikeCad_to_model_map.get(key, key)
            if model_key in self.default_values.keys():
                result_dict[model_key] = value
        return result_dict

    def handle_special_behavior(self, bikeCad_file_entries, result_dict):
        material_value = bikeCad_file_entries["MATERIAL"]
        self.handle_materials(result_dict, material_value)
        self.handle_keys_whose_presence_indicates_their_value(result_dict)

    def handle_materials(self, result_dict, materials_entry: str):
        result_dict[f"Material={materials_entry.lower().title()}"] = 1

    def handle_keys_whose_presence_indicates_their_value(self, result_dict):
        for key in keys_whose_presence_indicates_their_value:
            # TODO: ask Lyle whether it's a bug or a feature that CSB_Include is
            #  assigned to 0 in both the IF and ELSE clauses
            result_dict[key] = int(key in result_dict)

    def handle_ramifications(self, result_dict):
        if result_dict["CSB_Include"] == 0:
            result_dict["CSB_OD"] = 0.017759
        if result_dict["SSB_Include"] == 0:
            result_dict["SSB_OD"] = 0.015849

    def fill_default(self, result_dict):
        for key, value in self.default_values.items():
            if key not in result_dict:
                result_dict[key] = value

    def get_float_if_float(self, value):
        try:
            return float(value)
        except ValueError:
            return str(value).strip()
