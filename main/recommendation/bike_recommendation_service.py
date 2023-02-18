import os.path

import pandas as pd

from main.recommendation.similarity_engine import SimilarityEngine, EuclideanSimilarityEngine
from main.recommendation.similarity_engine_settings import EngineSettings
from main.processing.scaling_filter import ScalerWrapper
from main.resource_paths import RECOMMENDATION_DATASET_PATH
from main.processing.xml_handler import XmlHandler

SET_INVALID_TO_NAN = 'coerce'

FILENAME = 'filename'

SCALED_MEAN = 0


class DefaultBikeSettings(EngineSettings):
    light = ["Head tube upper extension2", "Seat tube extension2", "Head tube lower extension2",
             "Wheel width rear", "Wheel width front", "Head tube type", "BB length", "Head tube diameter",
             "Wheel cut", "BB diameter", "Seat tube diameter", "Top tube type", "CHAINSTAYbrdgdia1",
             "CHAINSTAYbrdgshift", "SEATSTAYbrdgdia1", "SEATSTAYbrdgshift", "bottle SEATTUBE0 show",
             "bottle DOWNTUBE0 show", "Front Fender include", "Rear Fender include", "Display RACK"]
    heavy = ["BB textfield", "Seat tube length", "Stack", "Seat angle", "CS textfield", "FCD textfield",
           "Head angle", "Saddle height", "Head tube length textfield", "ERD rear", "Dropout spacing style",
           "BSD front", "ERD front", "BSD rear", "Fork type", "Stem kind", "Display AEROBARS",
           "Handlebar style", "CHAINSTAYbrdgCheck", "SEATSTAYbrdgCheck", "Display WATERBOTTLES", "BELTorCHAIN",
           "Number of cogs", "Number of chainrings"]

    def max_n(self) -> int:
        return 10

    def include(self) -> list:
        return self.light + self.heavy

    def weights(self) -> dict:
        light_ = {key: 1 for key in self.light}
        heavy_ = {key: 3 for key in self.heavy}
        weights = light_
        weights.update(heavy_)
        return weights


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
    scaler = ScalerWrapper.build_from_dataframe(dataframe)
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
                 engine : SimilarityEngine = DEFAULT_ENGINE,
                 scaler: ScalerWrapper = DEFAULT_SCALER):
        self.scaler = scaler
        self.engine = engine
        self.xml_handler = XmlHandler()
    def recommend_bike(self, xml_user_entry: str):
        scaled_user_entry = self.pre_process_request(xml_user_entry)
        closest_bike_entry = self.engine.get_closest_index_to(scaled_user_entry)
        return self.grab_bike_file(closest_bike_entry)

    def pre_process_request(self, xml_user_entry):
        user_entry_dict = self.parse_xml_request(xml_user_entry)
        scaled_user_entry = self.scaler.scale(user_entry_dict)
        scaled_user_entry = self.default_to_mean(scaled_user_entry)
        return scaled_user_entry

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
        default_function = lambda x: float(x)
        function = self.enumeration_function_map.get(value, default_function)
        return function(value.lower())

    def default_to_mean(self, scaled_user_entry):
        for key in self.engine.get_settings().include():
            if key not in scaled_user_entry:
                scaled_user_entry[key] = SCALED_MEAN
        return scaled_user_entry

    def grab_bike_file(self, bike_filename):
        with open(os.path.join(os.path.dirname(__file__),
                               f"../resources/large/bikecad files/{bike_filename}"),
                  "r") as file:
            return file.read()
