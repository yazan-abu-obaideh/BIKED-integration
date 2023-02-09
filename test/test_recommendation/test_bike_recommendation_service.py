from main.recommendation.bike_recommendation_service import BikeRecommendationService
from main.xml_handler import XmlHandler
import unittest
import os

VALID_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../resources/bikes/(1).bcad")


class RecommendationServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = BikeRecommendationService()
        self.xml_handler = XmlHandler()

    def test_get_closest_to(self):
        with open(VALID_MODEL_PATH, 'r') as file:
            bike_in_request = file.read()
            recommended_bike = self.service.recommend_bike(bike_in_request)
        self.assertEqual(bike_in_request, recommended_bike)

    def test_replace_with_default(self):
        assert False

    def test_grab_bike_file(self):
        bike_file = self.service.grab_bike_file(1)
        self.xml_handler.set_xml(bike_file)
        self.assertGreater(len(self.xml_handler.get_entries_dict()), 25)

