from main.recommendation.bike_recommendation_service import BikeRecommendationService
from main.processing.bike_xml_handler import BikeXmlHandler
import unittest
import os

VALID_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../resources/bikes/(1).bcad")


class RecommendationServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = BikeRecommendationService()
        self.xml_handler = BikeXmlHandler()

    def test_get_closest_to(self):
        bike_in_request = self.__grab_bike_xml()
        recommended_bike = self.service.recommend_bike(bike_in_request)
        self.assertEqual(bike_in_request, recommended_bike)

    def test_raises_correct_exception(self):
        with self.assertRaises(ValueError) as context:
            self.service.recommend_bike("")
        self.assertEqual("Invalid BikeCAD file", context.exception.args[0])

    def __grab_bike_xml(self):
        with open(VALID_MODEL_PATH, 'r') as file:
            return file.read()

    def test_grab_bike_file(self):
        bike_file = self.service.grab_bike_file("(1).bcad")
        self.xml_handler.set_xml(bike_file)
        self.assertGreater(len(self.xml_handler.get_entries_dict()), 25)
