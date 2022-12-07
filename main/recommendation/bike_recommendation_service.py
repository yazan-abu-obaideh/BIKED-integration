from main.recommendation.recommendation_service_settings import RecommendationSettings
from main.recommendation.recommendation_service import RecommendationService
from main.xml_handler import XmlHandler
import pandas as pd
import os



class DefaultBikeSettings(RecommendationSettings):
    def __init__(self):
        self.maybe = ["Head tube upper extension2", "Seat tube extension2", "Head tube lower extension2", "Wheel width rear", "Wheel width front", "Head tube type", "BB length", "Head tube diameter", "Wheel cut", "BB diameter", "Seat tube diameter", "Top tube type", "CHAINSTAYbrdgdia1", "CHAINSTAYbrdgshift", "SEATSTAYbrdgdia1", "SEATSTAYbrdgshift", "bottle SEATTUBE0 show", "bottle DOWNTUBE0 show", "Front Fender include", "Rear Fender include", "Display RACK"]
        self.yes = ["BB textfield", "Seat tube length", "Stack", "Seat angle", "CS textfield", "FCD textfield", "Head angle", "Saddle height", "Head tube length textfield", "ERD rear", "Dropout spacing style", "BSD front", "ERD front", "BSD rear", "Fork type", "Stem kind", "Display AEROBARS", "Handlebar style", "CHAINSTAYbrdgCheck", "SEATSTAYbrdgCheck", "Display WATERBOTTLES", "BELTorCHAIN", "Number of cogs", "Number of chainrings"]

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
DEFAULT_DATASET = os.path.join(os.path.dirname(__file__), "../../resources/datasets/BIKED_recommend.csv")


class BikeRecommendationService:
    def __init__(self):
        self.inner_service = RecommendationService(pd.read_csv(DEFAULT_DATASET), DefaultBikeSettings())
        self.xml_handler = XmlHandler()
        num = 0
        for key in self.inner_service.settings.include():
            if key not in self.inner_service.data.columns.values:
                print(key)
                num += 1
        print(num)
        print(len(self.inner_service.settings.include()))
    def recommend_bike(self, xml_user_entry: str):
        self.xml_handler.set_xml(xml_user_entry)
        user_entry_dict = self.xml_handler.get_entries_dict()
        closest_bike = self.inner_service.get_closest_n(user_entry_dict, 1)
        self.xml_handler.set_entries_from_dict(closest_bike)
        return self.xml_handler.get_content_string()

if __name__ == "__main__":
    service = BikeRecommendationService()

