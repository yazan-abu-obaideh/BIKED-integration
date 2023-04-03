from src.main.processing.algebraic_parser import AlgebraicParser
from src.main.processing.bike_xml_handler import BikeXmlHandler
from src.main.evaluation.framed_mapper_settings import FramedMapperSettings
import numpy as np

from src.main.processing.request_pipeline import RequestPipeline

MILLIMETERS_TO_METERS_FACTOR = 1000


class FramedMapper:
    def __init__(self, settings: FramedMapperSettings):
        self.xml_handler = BikeXmlHandler()
        self.settings = settings
        # TODO: ensure adherence to T -> T
        self.pipeline = RequestPipeline([self.one_hot_encode,
                                         self.calculate_composite_values,
                                         self.map_to_model_input,
                                         self.handle_special_behavior,
                                         self.convert_millimeter_values_to_meters])

    def map_xml(self, xml: str):
        self.xml_handler.set_xml(xml)
        request_dict = self.xml_handler.get_entries_dict()
        return self.map_dict(request_dict)

    def map_dict(self, bikeCad_file_entries):
        return self.pipeline.pass_through(bikeCad_file_entries)

    def map_to_model_input(self, bikeCad_file_entries: dict) -> dict:
        keys_map = self.settings.get_bikeCad_to_model_map()
        valid_keys = list(self.settings.get_expected_input_keys())
        return {keys_map.get(key, key): value
                for key, value in bikeCad_file_entries.items()
                if keys_map.get(key, key) in valid_keys}

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

    def convert_millimeter_values_to_meters(self, result_dict: dict) -> dict:
        for key in self.should_be_converted(result_dict):
            result_dict[key] = self.convert_millimeter_value_to_meters(result_dict[key])
        return result_dict

    def should_be_converted(self, _dict):
        return (key for key in self.settings.millimeters_to_meters() if key in _dict.keys())

    def convert_millimeter_value_to_meters(self, original_value):
        return original_value / MILLIMETERS_TO_METERS_FACTOR

    def calculate_composite_values(self, bikeCad_file_entries: dict) -> dict:

        # TODO: homie this is essentially a bloated anonymous class. This is bad. Fix this.

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

    def __parse(self, value: str):
        if value.lower() in ["steel", "aluminum", "titanium"]:
            return value
        return AlgebraicParser().attempt_parse(value)

    def __key_filter(self, key):
        return key in list(self.settings.get_bikeCad_to_model_map().keys()) + ["MATERIAL"]

    def __value_filter(self, parsed_value):
        return parsed_value is not None
