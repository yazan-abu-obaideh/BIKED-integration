from main.recommendation.bike_recommendation_service import BikeRecommendationService
from main.xml_handler import XmlHandler
import unittest
import os

VALID_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../resources/bikes/FullModel1.xml")


class RecommendationServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = BikeRecommendationService()

    def test_get_closest_to(self):
        with open(VALID_MODEL_PATH, 'r') as file:
            self.service.recommend_bike(file.read())

    def test_grab_bike_file(self):
        bike_file = self.service.grab_bike_file(1)
        self.xml_handler.set_xml(bike_file)
        print(self.xml_handler.get_entries_dict())
        self.assertGreater(len(self.xml_handler.get_entries_dict()), 25)

