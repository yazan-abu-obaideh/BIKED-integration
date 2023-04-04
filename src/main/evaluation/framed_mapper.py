from typing import Optional

import numpy as np

from src.main.evaluation.framed_mapper_settings import FramedMapperSettings
from src.main.processing.bike_xml_handler import BikeXmlHandler
from src.main.processing.processing_pipeline import ProcessingPipeline

MILLIMETERS_TO_METERS_FACTOR = 1000


class FramedMapper:
    """Maps a dictionary representing
    a subset of bike properties into a dictionary representing
    a datapoint that wouldn't be out of place in the FRAMED dataset.
    If a value is not present the associated key will not be present in
    the returned dictionary. If a value X needed for
    the calculation of another value Y is not present, value Y and its
    associated key will not be present in the returned dictionary."""

    def __init__(self, settings: FramedMapperSettings):
        self.xml_handler = BikeXmlHandler()
        self.settings = settings
        # TODO: ensure adherence to T -> T
        self._mapping_pipeline = ProcessingPipeline([self._one_hot_encode,
                                                     self._calculate_composite_values,
                                                     self._map_to_model_input,
                                                     self._handle_special_behavior,
                                                     self._convert_millimeter_values_to_meters])

    def map_dict(self, bikeCad_file_entries):
        return self._mapping_pipeline.process(bikeCad_file_entries)

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
        accepted_values = ["STEEL", "ALUMINUM", "TITANIUM"]
        result_dict = self._add_if_valid(accepted_values, material_value, result_dict)
        return result_dict

    def _add_if_valid(self, accepted_values: list, material_value: str, result_dict: dict) -> dict:
        if material_value in accepted_values:
            result_dict[f"Material={material_value.lower().title()}"] = 1
        result_dict = self._set_other_values(accepted_values, material_value, result_dict)
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

    def _get_sum(self, my_dict, entries) -> Optional[float]:
        if self._any_key_missing(my_dict, entries):
            return None
        entries_values = [my_dict.get(entry, 0) for entry in entries]
        return sum(entries_values)

    def _get_average(self, my_dict, entries) -> Optional[float]:
        if self._any_key_missing(my_dict, entries):
            return None
        return self._get_sum(my_dict, entries) / len(entries)

    def _calculate_composite_values(self, bikeCad_file_entries: dict) -> dict:

        def set_optional_value(key, value):
            if value is not None:
                bikeCad_file_entries[key] = value

        set_optional_value('DT Length', self._calculate_dt_length(bikeCad_file_entries))

        set_optional_value('csd', self._get_average(bikeCad_file_entries,
                                                    ['Chain stay back diameter', 'Chain stay vertical diameter']))
        set_optional_value('ssd', self._get_average(bikeCad_file_entries,
                                                    ['Seat stay bottom diameter', 'SEATSTAY_HR']))
        set_optional_value('ttd', self._get_average(bikeCad_file_entries,
                                                    ['Top tube rear diameter', 'Top tube rear dia2',
                                                     'Top tube front diameter', 'Top tube front dia2']))
        set_optional_value('dtd',
                           self._get_average(bikeCad_file_entries, ['Down tube rear diameter', 'Down tube rear dia2',
                                                                    'Down tube front dia2',
                                                                    'Down tube front diameter']))

        bikeCad_file_entries['Wall thickness Bottom Bracket'] = 2.0
        bikeCad_file_entries['Wall thickness Head tube'] = 1.1
        return bikeCad_file_entries

    def _any_key_missing(self, dictionary, keys) -> bool:
        return not all([(key in dictionary) for key in keys])

    def _calculate_dt_length(self, bikeCad_file_entries) -> Optional[float]:
        required_keys = ['BB textfield', 'FCD textfield', 'FORKOR', 'FORK0L',
                         'Head tube lower extension2', 'lower stack height', 'Head angle']
        if self._any_key_missing(bikeCad_file_entries, required_keys):
            return None

        def geometric_average(entries):
            entries_squares = [bikeCad_file_entries.get(entry, 0) ** 2 for entry in entries]
            return np.power(sum(entries_squares), np.divide(1, len(entries)))

        def convert_angle(my_dict, entry):
            return my_dict[entry] * np.pi / 180

        fty = bikeCad_file_entries['BB textfield']
        ftx = geometric_average(['BB textfield', 'FCD textfield'])
        x = bikeCad_file_entries.get('FORKOR', 0)
        y = self._get_sum(bikeCad_file_entries, ['FORK0L', 'Head tube lower extension2', 'lower stack height'])
        ha = convert_angle(bikeCad_file_entries, 'Head angle')
        dtx = ftx - y * np.cos(ha) - x * np.sin(ha)
        dty = fty + y * np.sin(ha) + x * np.cos(ha)
        return np.sqrt(dtx ** 2 + dty ** 2)

    def _set_other_values(self, accepted_values: list, material_value: str, result_dict: dict) -> dict:
        for value in accepted_values:
            if value != material_value:
                result_dict[f"Material={value.lower().title()}"] = 0
        return result_dict
