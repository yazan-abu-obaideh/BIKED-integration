from main.recommendation.recommendation_service_settings import RecommendationSettings
from main.recommendation.recommendation_service import RecommendationService
from main.xml_handler import XmlHandler
import pandas as pd
import os



class DefaultBikeSettings(RecommendationSettings):
    def __init__(self):
        self._list = ['upper head tube ext', 'seat tube ext', 'lower head tube ext', 'Rear wheel width', 'Front wheel width',
                 'Head tube type', 'BB shell length', 'Head tube diam', 'Seat tube wheel cut', 'BB diameter',
                 'Seat tube diam', 'Top tube type', 'Chain Stay Bridge Diameter', 'Chain stay bridge to rear axle',
                 'seat stay bridge diam', 'seat stay bridge to rear axle', 'Seattube bottle?', 'Downtube bottle?',
                 'front fender?', 'rear fender?', 'racks?', 'BB drop', 'seat tube length c-t', 'stack', 'seat angle',
                 'chain stay length', 'front center distance', 'head angle', 'saddle height', 'Head tube length',
                 'Rear ERD', 'MTB/Road/Track', 'Front BSD', 'Front ERD', 'Rear BSD', 'Fork Type', 'Type of stem',
                 'Aerobars?', 'Handlebar style', 'Chain stay bridge?', 'Seat stay bridge?', 'Waterbottles?', 'Chain?',
                 '# cogs', '# chainrings']
        self.maybe = ["Head tube upper extension2", "Seat tube extension2", "Head tube lower extension2", "Wheel width rear", "Wheel width front", "Head tube type", "BB length", "Head tube diameter", "Wheel cut", "BB diameter", "Seat tube diameter", "Top tube type", "CHAINSTAYbrdgdia1", "CHAINSTAYbrdgshift", "SEATSTAYbrdgdia1", "SEATSTAYbrdgshift", "bottle SEATTUBE0 show", "bottle DOWNTUBE0 show", "Front Fender include", "Rear Fender include", "Display RACK"]
        self.yes = ["BB textfield", "Seat tube length", "Stack", "Seat angle", "CS textfield", "FCD textfield", "Head angle", "Saddle height", "Head tube length textfield", "ERD rear", "Dropout spacing style", "BSD front", "ERD front", "BSD rear", "Fork type", "Stem kind", "Display AEROBARS", "Handlebar style", "CHAINSTAYbrdgCheck", "SEATSTAYbrdgCheck", "Display WATERBOTTLES", "BELTorCHAIN", "Number of cogs", "Number of chainrings"]

    def max_n(self) -> int:
        return 10

    def include(self) -> list:
        return self._list

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
        num_not_included = 0
        for key in self.inner_service.settings.include():
            if key not in self.inner_service.data.columns.values:
                print(key)
                num_not_included += 1
        print(f"{num_not_included=}")
        num_included = len(self.inner_service.settings.include())
        print(f"{num_included=}")
    def recommend_bike(self, xml_user_entry: str):
        self.xml_handler.set_xml(xml_user_entry)
        user_entry_dict = self.xml_handler.get_entries_dict()
        self.warning = {}
        user_entry_dict = {key: self.enumerate(key, value) for key, value in user_entry_dict.items()}
        closest_bike = self.inner_service.get_closest_n(user_entry_dict, 1)[0]
        self.xml_handler.set_entries_from_dict(closest_bike)
        return self.xml_handler.get_content_string()

    def enumerate(self, key, value: str):
        value = value.lower()
        if value == 'true':
            return 1
        elif value == 'false':
            return 0
        else:
            try:
                return float(value)
            except ValueError:
                self.warning[key] = value
                return 0

if __name__ == "__main__":
    service = BikeRecommendationService()

