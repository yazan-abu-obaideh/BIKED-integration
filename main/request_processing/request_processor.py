from main.xml_handler import XmlHandler
from main.request_processing.request_processor_settings import RequestProcessorSettings
import numpy as np

from main.request_processing.request_pipeline import RequestPipeline

MILLIMETERS_TO_METERS_FACTOR = 1000


class RequestProcessor:
    def __init__(self, settings: RequestProcessorSettings):
        self.xml_handler = XmlHandler()
        self.settings = settings
        self.pipeline = RequestPipeline([self.parse_values,
                                         self.calculate_composite_values,
                                         self.one_hot_encode,
                                         self.map_to_model_input,
                                         self.handle_special_behavior,
                                         self.convert_millimeter_values_to_meters])

    def convert_xml(self, xml: str):
        self.xml_handler.set_xml(xml)
        request_dict = self.xml_handler.get_entries_dict()
        return self.convert_dict(request_dict)

    def convert_dict(self, bikeCad_file_entries):
        return self.pipeline.pass_through(bikeCad_file_entries)

    def map_to_model_input(self, bikeCad_file_entries: dict) -> dict:
        result_dict = {}
        for key, value in bikeCad_file_entries.items():
            model_key = self.settings.bikeCad_to_model_map().get(key, key)
            if self.valid_model_key(model_key):
                result_dict[model_key] = value
        return result_dict

    def valid_model_key(self, model_key):
        return model_key in self.settings.default_values().keys()

    def handle_special_behavior(self, result_dict: dict) -> dict:
        self.handle_keys_whose_presence_indicates_their_value(result_dict)
        self.handle_ramifications(result_dict)
        return result_dict

    def one_hot_encode(self, result_dict: dict) -> dict:
        result_dict[f"Material={result_dict['MATERIAL'].lower().title()}"] = 1
        return result_dict

    def handle_keys_whose_presence_indicates_their_value(self, result_dict):
        for key in self.settings.keys_whose_presence_indicates_their_value():
            result_dict[key] = int(key in result_dict)

    def handle_ramifications(self, result_dict):
        if result_dict["CSB_Include"] == 0:
            result_dict["CSB OD"] = 17.759
        if result_dict["SSB_Include"] == 0:
            result_dict["SSB OD"] = 15.849

    def parse_values(self, input_dict: dict) -> dict:
        return {key: self.get_float_or_strip(value) for key, value in input_dict.items()}

    def get_float_or_strip(self, value):
        try:
            return float(value)
        except ValueError:
            return str(value).strip()

    def convert_millimeter_values_to_meters(self, result_dict: dict) -> dict:
        for key in self.should_be_converted(result_dict):
            result_dict[key] = self.convert_millimeter_value_to_meters(result_dict[key])
        return result_dict

    def should_be_converted(self, _dict):
        return (key for key in self.settings.millimeters_to_meters() if key in _dict.keys())

    def convert_millimeter_value_to_meters(self, original_value):
        return original_value / MILLIMETERS_TO_METERS_FACTOR

    def calculate_composite_values(self, bikeCad_file_entries: dict) -> dict:

        def get_sum(entries):
            entries_values = [bikeCad_file_entries.get(entry, 0) for entry in entries]
            return sum(entries_values)

        def convert_angle(entry):
            return bikeCad_file_entries[entry] * np.pi / 180

        def get_average(entries):
            return get_sum(entries) / len(entries)

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
