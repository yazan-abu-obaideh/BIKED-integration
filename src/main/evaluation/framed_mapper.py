from src.main.processing.algebraic_parser import AlgebraicParser
from src.main.processing.bike_xml_handler import BikeXmlHandler
from src.main.evaluation.framed_mapper_settings import FramedMapperSettings
import numpy as np

from src.main.processing.request_pipeline import RequestPipeline

MILLIMETERS_TO_METERS_FACTOR = 1000


class FramedMapper:
    """Maps a dictionary representing
    a subset of bike properties into a dictionary representing
    a datapoint that belongs to the FRAMED dataset.
    If a value is not present the associated key will not be present in
    the returned dictionary. If a value X needed for
    the calculation of another value Y is not present, value Y and its
    associated key will not be present in the returned dictionary."""

    def __init__(self, settings: FramedMapperSettings):
        self.xml_handler = BikeXmlHandler()
        self.settings = settings
        # TODO: ensure adherence to T -> T
        self.pipeline = RequestPipeline([self._one_hot_encode,
                                         self._calculate_composite_values,
                                         self._map_to_model_input,
                                         self._handle_special_behavior,
                                         self._convert_millimeter_values_to_meters])

    def map_dict(self, bikeCad_file_entries):
        return self.pipeline.pass_through(bikeCad_file_entries)

    def _map_to_model_input(self, bikeCad_file_entries: dict) -> dict:
        keys_map = self.settings.get_bikeCad_to_model_map()
        valid_keys = list(self.settings.get_expected_input_keys())
        return {keys_map.get(key, key): value
                for key, value in bikeCad_file_entries.items()
                if keys_map.get(key, key) in valid_keys}

    def _handle_special_behavior(self, result_dict: dict) -> dict:
        self._handle_keys_whose_presence_indicates_their_value(result_dict)
        self._handle_ramifications(result_dict)
        return result_dict

    def _one_hot_encode(self, result_dict: dict) -> dict:
        material_value = result_dict.get("MATERIAL", None)
        if material_value in ["STEEL", "ALUMINUM", "TITANIUM"]:
            result_dict[f"Material={result_dict['MATERIAL'].lower().title()}"] = 1
        return result_dict

    def _handle_keys_whose_presence_indicates_their_value(self, result_dict):
        for key in self.settings.keys_whose_presence_indicates_their_value():
            result_dict[key] = int(key in result_dict)

    def _handle_ramifications(self, result_dict):
        if result_dict.get("CSB_Include", 1) == 0:
            result_dict["CSB OD"] = 17.759
        if result_dict.get("SSB_Include", 1) == 0:
            result_dict["SSB OD"] = 15.849

    def _convert_millimeter_values_to_meters(self, result_dict: dict) -> dict:
        for key in self._should_be_converted(result_dict):
            original_value = result_dict[key]
            result_dict[key] = original_value / MILLIMETERS_TO_METERS_FACTOR
        return result_dict

    def _should_be_converted(self, _dict):
        return (key for key in self.settings.millimeters_to_meters() if key in _dict.keys())

    def _get_sum(self, entries, my_dict):
        entries_values = [my_dict.get(entry, 0) for entry in entries]
        return sum(entries_values)

    def _convert_angle(self, entry, my_dict):
        return my_dict[entry] * np.pi / 180

    def _get_average(self, my_dict, entries):
        # for entry in entries:
        #     if entry not in bikeCad_file_entries:
        #         return None
        return self._get_sum(entries, my_dict) / len(entries)

    def _get_geometric_average(self, entries, my_dict):
        # for entry in entries:
        #     if entry not in bikeCad_file_entries:
        #         return None
        entries_squares = [my_dict.get(entry, 0) ** 2 for entry in entries]
        return np.power(sum(entries_squares), np.divide(1, len(entries)))

    def _calculate_composite_values(self, bikeCad_file_entries: dict) -> dict:

        # TODO: homie this is essentially a bloated anonymous class. This is bad. Fix this.
        def set_value(key, value):
            if value is not None:
                bikeCad_file_entries[key] = value

        set_value('DT Length', self._calculate_dt_length(bikeCad_file_entries))

        set_value('csd', self._get_average(bikeCad_file_entries,
                                           ['Chain stay back diameter', 'Chain stay vertical diameter']))
        set_value('ssd', self._get_average(bikeCad_file_entries,
                                           ['Seat stay bottom diameter', 'SEATSTAY_HR']))
        set_value('ttd', self._get_average(bikeCad_file_entries,
                                           ['Top tube rear diameter', 'Top tube rear dia2',
                                            'Top tube front diameter', 'Top tube front dia2']))
        set_value('dtd', self._get_average(bikeCad_file_entries, ['Down tube rear diameter', 'Down tube rear dia2',
                                                                  'Down tube front dia2', 'Down tube front diameter']))

        bikeCad_file_entries['Wall thickness Bottom Bracket'] = 2.0
        bikeCad_file_entries['Wall thickness Head tube'] = 1.1
        return bikeCad_file_entries

    def _calculate_dt_length(self, bikeCad_file_entries):
        fty = bikeCad_file_entries['BB textfield']
        ftx = self._get_geometric_average(['BB textfield', 'FCD textfield'], bikeCad_file_entries)
        x = bikeCad_file_entries.get('FORKOR', 0)
        y = self._get_sum(['FORK0L', 'Head tube lower extension2', 'lower stack height'], bikeCad_file_entries)
        ha = self._convert_angle('Head angle', bikeCad_file_entries)
        dtx = ftx - y * np.cos(ha) - x * np.sin(ha)
        dty = fty + y * np.sin(ha) + x * np.cos(ha)
        return np.sqrt(dtx ** 2 + dty ** 2)

    def __parse(self, value: str):
        if value.lower() in ["steel", "aluminum", "titanium"]:
            return value
        return AlgebraicParser().attempt_parse(value)

    def __key_filter(self, key):
        return key in list(self.settings.get_bikeCad_to_model_map().keys()) + ["MATERIAL"]

    def __value_filter(self, parsed_value):
        return parsed_value is not None
