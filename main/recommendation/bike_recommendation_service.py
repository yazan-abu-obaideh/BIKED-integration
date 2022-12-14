from main.recommendation.recommendation_service_settings import RecommendationSettings
from main.recommendation.recommendation_service import RecommendationService
from main.xml_handler import XmlHandler
import pandas as pd
import os

from request_processing.scaler_wrapper import ScalerWrapper


class DefaultBikeSettings(RecommendationSettings):
    def __init__(self):
        self.maybe = ["Head tube upper extension2", "Seat tube extension2", "Head tube lower extension2",
                      "Wheel width rear", "Wheel width front", "Head tube type", "BB length", "Head tube diameter",
                      "Wheel cut", "BB diameter", "Seat tube diameter", "Top tube type", "CHAINSTAYbrdgdia1",
                      "CHAINSTAYbrdgshift", "SEATSTAYbrdgdia1", "SEATSTAYbrdgshift", "bottle SEATTUBE0 show",
                      "bottle DOWNTUBE0 show", "Front Fender include", "Rear Fender include", "Display RACK"]
        self.yes = ["BB textfield", "Seat tube length", "Stack", "Seat angle", "CS textfield", "FCD textfield",
                    "Head angle", "Saddle height", "Head tube length textfield", "ERD rear", "Dropout spacing style",
                    "BSD front", "ERD front", "BSD rear", "Fork type", "Stem kind", "Display AEROBARS",
                    "Handlebar style", "CHAINSTAYbrdgCheck", "SEATSTAYbrdgCheck", "Display WATERBOTTLES", "BELTorCHAIN",
                    "Number of cogs", "Number of chainrings"]

    def max_n(self) -> int:
        return 10

    def include(self) -> list:
        return  self.maybe + self.yes

    def weights(self) -> dict:
        maybe_weights = {key: 1 for key in self.maybe}
        yes_weights = {key: 3 for key in self.yes}
        weights = maybe_weights
        weights.update(yes_weights)
        return weights


DEFAULT_SETTINGS = DefaultBikeSettings()
DEFAULT_DATASET = os.path.join(os.path.dirname(__file__), "../../resources/datasets/BIKED_recommend.csv")


class BikeRecommendationService:
    def __init__(self, settings: RecommendationSettings = DEFAULT_SETTINGS, data_file_path=DEFAULT_DATASET):
        dataframe = pd.read_csv(data_file_path)
        self.scaler = ScalerWrapper.build_from_dataframe(dataframe)
        self.inner_service = RecommendationService(
            dataframe,
            settings)
        self.xml_handler = XmlHandler()
        self.log_initialization()

    def log_initialization(self):
        num_not_included = 0
        for key in self.inner_service.settings.include():
            if key not in [value.lower() for value in list(self.inner_service.data.columns.values)]:
                print(key)
                num_not_included += 1
        print(f"{num_not_included=}")
        max_num_included = len(self.inner_service.settings.include())
        print(f"{max_num_included=}")

    def recommend_bike(self, xml_user_entry: str):
        self.xml_handler.set_xml(xml_user_entry)
        user_entry_dict = self.xml_handler.get_entries_dict()
        user_entry_dict = {key: self.enumerate(value) for key, value in user_entry_dict.items()}
        closest_bike = self.inner_service.get_closest_n(user_entry_dict, 1)[0]
        self.xml_handler.set_entries_from_dict(closest_bike)
        return self.xml_handler.get_content_string()

    def enumerate(self, value: str):
        values_map = {
            'true': lambda x: 1,
            'false': lambda x: 0
        }
        return values_map.get(value, self.parse_possible_float)(value)

    def parse_possible_float(self, f) -> float:
        try:
            return float(f)
        except ValueError:
            return 0


if __name__ == "__main__":
    service = BikeRecommendationService()
