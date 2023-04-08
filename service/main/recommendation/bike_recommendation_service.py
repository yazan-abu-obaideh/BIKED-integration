import pandas as pd

from service.main.processing.dictionary_handler import DictionaryHandler
from service.main.processing.algebraic_parser import AlgebraicParser
from service.main.processing.request_validator import RequestValidator
from service_resources.resource_paths import RECOMMENDATION_DATASET_PATH
from service.main.processing.bike_xml_handler import BikeXmlHandler
from service.main.processing.scaling_filter import ScalingFilter
from service.main.recommendation.default_engine_settings import DefaultBikeSettings
from service.main.recommendation.similarity_engine import SimilarityEngine, EuclideanSimilarityEngine

SET_INVALID_TO_NAN = 'coerce'

FILENAME = 'filename'

SCALED_MEAN = 0

DEFAULT_SETTINGS = DefaultBikeSettings()


def to_numeric_except_index(dataframe):
    for column in dataframe.columns.values:
        if column != FILENAME:
            dataframe[column] = pd.to_numeric(dataframe[column], errors=SET_INVALID_TO_NAN)


def prepare_dataframe_and_scaler(data_file_path, settings):
    dataframe = pd.read_csv(data_file_path)
    dataframe.set_index(FILENAME, inplace=True)
    dataframe.drop(columns=dataframe.columns.difference(settings.include() + [FILENAME]), inplace=True)
    to_numeric_except_index(dataframe)
    scaler = ScalingFilter.build_from_dataframe(dataframe)
    scaled_dataframe = scaler.scale_dataframe(dataframe).fillna(value=SCALED_MEAN)
    return scaled_dataframe, scaler


DEFAULT_DATAFRAME, DEFAULT_SCALER = prepare_dataframe_and_scaler(RECOMMENDATION_DATASET_PATH, DEFAULT_SETTINGS)
DEFAULT_ENGINE = EuclideanSimilarityEngine(DEFAULT_DATAFRAME, DEFAULT_SETTINGS)


class BikeRecommendationService:

    def __init__(self,
                 engine: SimilarityEngine = DEFAULT_ENGINE,
                 scaler: ScalingFilter = DEFAULT_SCALER):
        self.scaler = scaler
        self.engine = engine
        self.request_validator = RequestValidator()
        self.parser = AlgebraicParser()
        self.dict_handler = DictionaryHandler()

    def recommend_bike_from_xml(self, xml_request: str):
        return {"similarBikes": [self._recommend_bike_from_parsed_dict(self._parse_to_dict(xml_request))],
                "warnings": []}

    def _parse_to_dict(self, xml: str) -> dict:
        xml_handler = BikeXmlHandler()
        xml_handler.set_xml(xml)
        all_entries = xml_handler.get_entries_dict()
        filtered_by_keys = self.dict_handler.filter_keys(all_entries, self._key_filter)
        parsed = self.dict_handler.parse_values(filtered_by_keys, self.parser.attempt_parse)
        filtered_by_values = self.dict_handler.filter_values(parsed, self._value_filter)
        return filtered_by_values

    def _recommend_bike_from_parsed_dict(self, user_entry: dict):
        self.request_validator.raise_if_empty(user_entry, "Invalid BikeCAD file")
        scaled_user_entry = self._pre_process_request(user_entry)
        closest_bike_entry = self.engine.get_closest_index_to(scaled_user_entry)
        return self._build_link(closest_bike_entry)

    def _pre_process_request(self, request: dict):
        scaled = self.scaler.scale(request)
        return self._default_to_mean(scaled)

    def _default_to_mean(self, scaled_user_entry):
        for key in self.engine.get_settings().include():
            if key not in scaled_user_entry:
                scaled_user_entry[key] = SCALED_MEAN
        return scaled_user_entry

    def _build_link(self, bike_filename):
        return f"http://bcd.bikecad.ca/{bike_filename}"

    def _key_filter(self, key):
        return key in self.engine.get_settings().include()

    def _value_filter(self, value):
        return value is not None and self._valid_numeric(value)

    def _valid_numeric(self, value):
        return (type(value) in [float, int]) and (value not in [float("-inf"), float("inf")])
