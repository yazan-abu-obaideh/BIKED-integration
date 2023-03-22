import os.path

import pandas as pd

from src.main.processing.bike_xml_handler import BikeXmlHandler
from src.main.processing.scaling_filter import ScalingFilter
from src.main.recommendation.default_engine_settings import DefaultBikeSettings
from src.main.recommendation.similarity_engine import SimilarityEngine, EuclideanSimilarityEngine
from service_resources.resource_paths import RECOMMENDATION_DATASET_PATH

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
    enumeration_function_map = {
        'true': lambda x: 1,
        'false': lambda x: 0
    }

    def __init__(self,
                 engine: SimilarityEngine = DEFAULT_ENGINE,
                 scaler: ScalingFilter = DEFAULT_SCALER):
        self.scaler = scaler
        self.engine = engine
        self.xml_handler = BikeXmlHandler()

    def recommend_bike(self, xml_user_entry: str):
        scaled_user_entry = self.pre_process_request(xml_user_entry)
        closest_bike_entry = self.engine.get_closest_index_to(scaled_user_entry)
        return self.build_link(closest_bike_entry)

    def pre_process_request(self, xml_user_entry):
        user_entry_dict = self.parse_xml_request(xml_user_entry)
        scaled_user_entry = self.scaler.scale(user_entry_dict)
        processed_user_entry = self.default_to_mean(scaled_user_entry)
        return processed_user_entry

    def parse_xml_request(self, xml_user_entry):
        self.xml_handler.set_xml(xml_user_entry)
        user_entry_dict = {key: value for key, value in self.xml_handler.get_entries_dict().items()
                           if key in self.engine.get_settings().include()}
        if len(user_entry_dict) == 0:
            raise ValueError("Invalid BikeCAD file")
        keys = list(user_entry_dict.keys())
        for key in keys:
            try:
                user_entry_dict[key] = self.attempt_enumerate(user_entry_dict[key])
            except ValueError:
                del user_entry_dict[key]
        return user_entry_dict

    def attempt_enumerate(self, value: str):
        def default_function(x): return float(x)
        function = self.enumeration_function_map.get(value, default_function)
        return function(value.lower())

    def default_to_mean(self, scaled_user_entry):
        for key in self.engine.get_settings().include():
            if key not in scaled_user_entry:
                scaled_user_entry[key] = SCALED_MEAN
        return scaled_user_entry

    def build_link(self, bike_filename):
        return f"http://bcd.bikecad.ca/{bike_filename}"
