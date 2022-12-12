from main.xml_handler import XmlHandler
from main.request_processing.request_adapter_settings import RequestAdapterSettings
import numpy as np


class RequestAdapter:
    def __init__(self, settings: RequestAdapterSettings):
        self.xml_handler = XmlHandler()
        self.settings = settings

    def convert_xml(self, raw_xml: str) -> dict:
        bikeCad_file_entries = self.get_dict_from(raw_xml)
        self.raise_if_empty_dict(bikeCad_file_entries)
        return self.convert_dict(bikeCad_file_entries)

    def convert_dict(self, bikeCad_file_entries):
        result_dict = self.parse_values(bikeCad_file_entries)
        result_dict = self.calculate_composite_values(result_dict)
        result_dict = self.map_to_model_input(result_dict)
        self.handle_special_behavior(bikeCad_file_entries, result_dict)
        self.convert_units(result_dict)
        return result_dict

    def raise_if_empty_dict(self, bikeCad_file_entries):
        if len(bikeCad_file_entries) == 0:
            raise ValueError('Invalid BikeCAD file')

    def get_dict_from(self, raw_xml):
        self.xml_handler.set_xml(raw_xml)
        bikeCad_file_entries = self.xml_handler.get_entries_dict()
        return bikeCad_file_entries

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
            result_dict[key] = int(key in result_dict)

    def handle_ramifications(self, result_dict):
        if result_dict["CSB_Include"] == 0:
            result_dict["CSB OD"] = 17.759
        if result_dict["SSB_Include"] == 0:
            result_dict["SSB OD"] = 15.849

    def fill_default(self, result_dict):
        for key, value in self.settings.default_values().items():
            if key not in result_dict:
                result_dict[key] = value

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
        def get_average(entries):
            entries_values = [bikeCad_file_entries.get(entry, 0) for entry in entries]
            return sum(entries_values)/len(entries)

        bbd = bikeCad_file_entries['BB textfield']
        fcd = bikeCad_file_entries['FCD textfield']
        fty = bbd
        ftx = np.sqrt(fty ** 2 + fcd ** 2)
        x = bikeCad_file_entries.get('FORKOR', 0)
        fkl = bikeCad_file_entries['FORK0L']
        htlx = bikeCad_file_entries['Head tube lower extension2']
        lsth = bikeCad_file_entries.get('lower stack height', 0)
        y = fkl + htlx + lsth
        ha = bikeCad_file_entries['Head angle'] * np.pi / 180
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
