from main.xml_handler import XmlHandler
from main.request_processing.request_adapter_settings import RequestAdapterSettings
import numpy as np


class RequestAdapter:
    def __init__(self, settings: RequestAdapterSettings):
        self.xml_handler = XmlHandler()
        self.settings = settings

    def convert_dict(self, bikeCad_file_entries):
        result_dict = self.parse_values(bikeCad_file_entries)
        result_dict = self.calculate_composite_values(result_dict)
        result_dict = self.map_to_model_input(result_dict)
        self.handle_special_behavior(bikeCad_file_entries["MATERIAL"], result_dict)
        self.convert_units(result_dict)
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

    def handle_special_behavior(self, materials_entry, result_dict):
        self.one_hot_encode(result_dict, materials_entry)
        self.handle_keys_whose_presence_indicates_their_value(result_dict)
        self.handle_ramifications(result_dict)

    def one_hot_encode(self, result_dict, materials_entry: str):
        result_dict[f"Material={materials_entry.lower().title()}"] = 1

    def handle_keys_whose_presence_indicates_their_value(self, result_dict):
        for key in self.settings.keys_whose_presence_indicates_their_value():
            result_dict[key] = int(key in result_dict)

    def handle_ramifications(self, result_dict):
        if result_dict["CSB_Include"] == 0:
            result_dict["CSB OD"] = 17.759
        if result_dict["SSB_Include"] == 0:
            result_dict["SSB OD"] = 15.849

    def fill_default_and_return_defaulted_values(self, result_dict) -> list:
        defaulted_values = []
        for key, value in self.settings.default_values().items():
            if key not in result_dict:
                result_dict[key] = value
                defaulted_values.append(key)
        return defaulted_values


    def parse_values(self, result_dict) -> dict:
        return {key: self.get_float_or_strip(value) for key, value in result_dict.items()}

    def get_float_or_strip(self, value):
        try:
            return float(value)
        except ValueError:
            return str(value).strip()

    def convert_units(self, result_dict):
        for key, divider in self.settings.unit_conversion_division_dict().items():
            self.convert_unit_if_valid_key(divider, key, result_dict)

    def convert_unit_if_valid_key(self, divider, key, result_dict):
        if key in result_dict:
            result_dict[key] = result_dict[key] / divider

    def calculate_composite_values(self, bikeCad_file_entries):

        def get_sum(entries):
            entries_values = [bikeCad_file_entries.get(entry, 0) for entry in entries]
            return sum(entries_values)

        def convert_angle(entry):
            return bikeCad_file_entries[entry] * np.pi / 180

        def get_average(entries):
            return get_sum(entries)/len(entries)

        def get_geometric_average(entries):
            entries_squares = [bikeCad_file_entries.get(entry, 0) ** 2 for entry in entries]
            return np.power(sum(entries_squares), np.divide(1, len(entries)))

        fty = bikeCad_file_entries['BB textfield']
        ftx = get_geometric_average(['BB textfield', 'FCD textfield'])
        x = bikeCad_file_entries.get('FORKOR', 0)
        y = get_sum(['FORK0L', 'Head tube lower extension2', 'lower stack height'])
        ha = convert_angle('Head angle')
        dtx = ftx - y * np.cos(ha) - x * np.sin(ha)
        dty = fty + y * np.sin(ha) + x * np.cos(ha)

        bikeCad_file_entries['DT Length'] = np.sqrt(dtx ** 2 + dty ** 2)

        bikeCad_file_entries['csd'] = get_average(['Chain stay back diameter', 'Chain stay vertical diameter'])

        bikeCad_file_entries['ssd'] = get_average(['Seat stay bottom diameter', 'SEATSTAY_HR'])

        bikeCad_file_entries['ttd'] = get_average(['Top tube rear diameter', 'Top tube rear dia2',
                                                   'Top tube front diameter', 'Top tube front dia2'])

        bikeCad_file_entries['dtd'] = get_average(['Down tube rear diameter', 'Down tube rear dia2',
                                                   'Down tube front dia2', 'Down tube front diameter'])

        bikeCad_file_entries['Wall thickness Bottom Bracket'] = 2.0
        bikeCad_file_entries['Wall thickness Head tube'] = 1.1
        return bikeCad_file_entries
