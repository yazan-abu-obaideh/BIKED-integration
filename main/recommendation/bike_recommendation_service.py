import logging
import os.path

import pandas as pd

from main.recommendation.recommendation_service import RecommendationService
from main.recommendation.recommendation_service_settings import RecommendationSettings
from main.request_processing.scaler_wrapper import ScalerWrapper
from main.resource_paths import RECOMMENDATION_DATASET_PATH
from main.xml_handler import XmlHandler

SCALED_MEAN = 0


class DefaultBikeSettings(RecommendationSettings):
    maybe = ["Head tube upper extension2", "Seat tube extension2", "Head tube lower extension2",
             "Wheel width rear", "Wheel width front", "Head tube type", "BB length", "Head tube diameter",
             "Wheel cut", "BB diameter", "Seat tube diameter", "Top tube type", "CHAINSTAYbrdgdia1",
             "CHAINSTAYbrdgshift", "SEATSTAYbrdgdia1", "SEATSTAYbrdgshift", "bottle SEATTUBE0 show",
             "bottle DOWNTUBE0 show", "Front Fender include", "Rear Fender include", "Display RACK"]
    yes = ["BB textfield", "Seat tube length", "Stack", "Seat angle", "CS textfield", "FCD textfield",
           "Head angle", "Saddle height", "Head tube length textfield", "ERD rear", "Dropout spacing style",
           "BSD front", "ERD front", "BSD rear", "Fork type", "Stem kind", "Display AEROBARS",
           "Handlebar style", "CHAINSTAYbrdgCheck", "SEATSTAYbrdgCheck", "Display WATERBOTTLES", "BELTorCHAIN",
           "Number of cogs", "Number of chainrings"]

    def max_n(self) -> int:
        return 10

    def include(self) -> list:
        return self.maybe + self.yes

    def weights(self) -> dict:
        maybe_weights = {key: 1 for key in self.maybe}
        yes_weights = {key: 3 for key in self.yes}
        weights = maybe_weights
        weights.update(yes_weights)
        return weights


DEFAULT_SETTINGS = DefaultBikeSettings()


class BikeRecommendationService:
    enumeration_function_map = {
        'true': lambda x: 1,
        'false': lambda x: 0
    }

    def __init__(self, settings: RecommendationSettings = DEFAULT_SETTINGS,
                 data_file_path=RECOMMENDATION_DATASET_PATH):
        # LOAD INDICES
        dataframe = pd.read_csv(data_file_path)
        dataframe.drop(columns=dataframe.columns.difference(settings.include()), inplace=True)
        self.scaler = ScalerWrapper.build_from_dataframe(dataframe)
        self.inner_service = RecommendationService(
            self.scaler.scale_dataframe(dataframe),
            settings)
        self.xml_handler = XmlHandler()
        # TODO: aspect-oriented programming.
        self.log_initialization()

    def log_initialization(self):
        desired = self.inner_service.settings.include()
        actual = self.inner_service.data.columns.values
        if not set(desired).issubset(set(actual)):
            logging.log(level=logging.CRITICAL,
                        msg="WARNING: BikeRecommendationService configured incorrectly." +
                            " Columns included in the settings do not match dataset columns.")

    def recommend_bike(self, xml_user_entry: str):
        scaled_user_entry = self.pre_process_request(xml_user_entry)
        closest_bike_index = self.inner_service.get_closest_index_to(scaled_user_entry)
        return self.grab_bike_file(closest_bike_index)

    def pre_process_request(self, xml_user_entry):
        user_entry_dict = self.parse_xml_request(xml_user_entry)
        scaled_user_entry = self.scaler.scale(user_entry_dict)
        scaled_user_entry = self.default_to_mean(scaled_user_entry)
        return scaled_user_entry

    def parse_xml_request(self, xml_user_entry):
        self.xml_handler.set_xml(xml_user_entry)
        user_entry_dict = self.xml_handler.get_entries_dict()
        return {key: self.attempt_enumerate(value) for key, value in user_entry_dict.items()}

    def default_to_mean(self, scaled_user_entry):
        for key in self.inner_service.settings.include():
            if key not in scaled_user_entry:
                scaled_user_entry[key] = SCALED_MEAN
        return scaled_user_entry

    def attempt_enumerate(self, value: str):
        default_function = self.parse_optional_float
        function = self.enumeration_function_map.get(value, default_function)
        return function(value)

    def parse_optional_float(self, f) -> float:
        try:
            return float(f)
        except ValueError:
            return 0

    def grab_bike_file(self, bike_index):
        with open(os.path.join(os.path.dirname(__file__),
                               f"../resources/large/bikecad files/({bike_index}).bcad"),
                  "r") as file:
            return file.read()
