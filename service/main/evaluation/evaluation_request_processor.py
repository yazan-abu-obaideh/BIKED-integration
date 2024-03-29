from typing import Optional

import numpy as np

from service.main.processing.dictionary_handler import DictionaryHandler
from service.main.processing.algebraic_parser import AlgebraicParser
from service.main.processing.request_validator import RequestValidator
from service.main.processing.scaling_filter import ScalingFilter
from service.main.evaluation.request_processor_settings import RequestProcessorSettings
from service.main.processing.bike_xml_handler import BikeXmlHandler
from service.main.processing.processing_pipeline import ProcessingPipeline

MILLIMETERS_TO_METERS_FACTOR = 1000
SCALED_MEAN = 0


class EvaluationRequestProcessor:
    def __init__(self, request_scaler: ScalingFilter, settings: RequestProcessorSettings):
        self._settings = settings
        self._request_scaler = request_scaler
        self._request_validator = RequestValidator()
        self._parser = AlgebraicParser()
        self._dict_handler = DictionaryHandler()
        self._dict_to_model_input_pipeline = ProcessingPipeline(steps=[
            self._convert_to_legacy_format,
            self._filter_keys,
            self._parse_values,
            self._filter_values,
            self._perform_preliminary_validations,
            self._one_hot_encode,
            self._validate_datatypes,
            self._calculate_composite_values,
            self._map_to_model_input,
            self._handle_special_behavior,
            self._convert_millimeter_values_to_meters,
            self._request_scaler.scale,
            self._default_none_to_mean,
        ])
        self._xml_to_model_input_pipeline = ProcessingPipeline(steps=[
            self._xml_to_dict,
            self._dict_to_model_input_pipeline.process
        ])

    def map_to_validated_model_input(self, xml: str) -> dict:
        return self._xml_to_model_input_pipeline.process(xml)

    def map_dict_to_validated_model_input(self, dictionary: dict) -> dict:
        return self._dict_to_model_input_pipeline.process(dictionary)

    def _xml_to_dict(self, xml_user_request):
        xml_handler = BikeXmlHandler()
        xml_handler.set_xml(xml_user_request)
        return xml_handler.get_entries_dict()

    def _perform_preliminary_validations(self, user_request):
        self._request_validator.raise_if_empty(user_request, 'Invalid BikeCAD file')
        self._request_validator.raise_if_does_not_contain(user_request, ["MATERIAL"])
        return user_request

    def _default_none_to_mean(self, bike_cad_dict):
        defaulted_keys = self._get_empty_keys(bike_cad_dict)
        for key in defaulted_keys:
            bike_cad_dict[key] = SCALED_MEAN
        return bike_cad_dict

    def _map_to_model_input(self, bikeCad_file_entries: dict) -> dict:
        keys_map = self._settings.bikeCad_to_model_map()
        valid_keys = list(self._settings.expected_input_keys())
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
        result_dict.pop("MATERIAL", None)
        return result_dict

    def _convert_to_legacy_format(self, result_dict: dict):
        for butted_key, legacy_key in self._settings.butted_wall_map().items():
            is_post_version20point1 = self._is_post_version20point1(butted_key, result_dict)
            if is_post_version20point1 is not None:
                self._to_legacy(butted_key, legacy_key, is_post_version20point1, result_dict)
        return result_dict

    def _is_post_version20point1(self, butted_key, result_dict):
        is_post_version20point1 = result_dict.get(self._settings.is_butted_template(butted_key))
        return is_post_version20point1

    def _to_legacy(self, butted_key, default_key, is_post_version20point1, result_dict):
        is_butted_parsed = self._parser.attempt_parse(is_post_version20point1)
        wall_pair = self._settings.wall_pair_templates(butted_key)
        if is_butted_parsed:
            result_dict[default_key] = result_dict[wall_pair[1]]
        else:
            result_dict[default_key] = result_dict[wall_pair[0]]

    def _validate_datatypes(self, result_dict: dict) -> dict:
        self._raise_if_invalid_types(result_dict)
        return result_dict

    def _get_empty_keys(self, bike_cad_dict):
        return (key for key in self._settings.expected_input_keys() if key not in bike_cad_dict)

    def _raise_if_invalid_types(self, result_dict: dict):
        for key, value in result_dict.items():
            self._raise_if_invalid_type(key, value)

    def _raise_if_invalid_type(self, key, value):
        if type(value) not in [float, int]:
            raise ValueError(f"Failed to parse value: [{value}] - value was associated with key: [{key}]")

    def _add_if_valid(self, accepted_values: list, material_value: str, result_dict: dict) -> dict:
        if material_value in accepted_values:
            result_dict[f"Material={material_value.lower().title()}"] = 1
        result_dict = self._set_other_values(accepted_values, material_value, result_dict)
        return result_dict

    def _handle_keys_whose_presence_indicates_their_value(self, result_dict):
        for key in self._settings.keys_whose_presence_indicates_their_value():
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
        return (key for key in self._settings.millimeters_to_meters() if key in _dict.keys())

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

    def _parse_values(self, dictionary: dict):
        return self._dict_handler.parse_values(dictionary, self._parser.attempt_parse)

    def _filter_keys(self, dictionary: dict):
        return self._dict_handler.filter_keys(dictionary, self._key_filter)

    def _filter_values(self, dictionary: dict):
        return self._dict_handler.filter_values(dictionary, self._value_filter)

    def _key_filter(self, key: str):
        return key in self._settings.expected_xml_keys()

    def _value_filter(self, parsed_value):
        return parsed_value is not None and self._valid_if_numeric(parsed_value)

    def _valid_if_numeric(self, parsed_value):
        if type(parsed_value) in [float, int]:
            return parsed_value not in [float("-inf"), float("inf")]
        return True
