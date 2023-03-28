from src.main.recommendation.bike_recommendation_service import BikeRecommendationService
from src.main.processing.bike_xml_handler import BikeXmlHandler
import unittest
import os

VALID_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../resources/bikes/1310591065335.bcad")


class RecommendationServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = BikeRecommendationService()
        self.xml_handler = BikeXmlHandler()

    @unittest.skip
    def test_request_with_bad_datatypes(self):
        pass

    @unittest.skip
    def test_empty_request(self):
        pass

    @unittest.skip
    def test_request_with_extreme_values(self):
        pass

    @unittest.skip
    def test_request_with_none_values(self):
        pass

    @unittest.skip
    def test_request_with_duplicated_keys(self):
        pass

    def test_get_closest_to(self):
        bike_in_request = self.__grab_bike_xml()
        recommended_bike = self.service.recommend_bike_from_xml(bike_in_request)
        self.assertEqual("http://bcd.bikecad.ca/1310591065335.bcad", recommended_bike)

    def test_raises_correct_exception(self):
        with self.assertRaises(ValueError) as context:
            self.service.recommend_bike_from_xml("")
        self.assertEqual("Invalid BikeCAD file", context.exception.args[0])

    def __grab_bike_xml(self):
        with open(VALID_MODEL_PATH, 'r') as file:
            return file.read()

    def test_buildlink(self):
        self.assertEqual("http://bcd.bikecad.ca/1.bcad", self.service.build_link("1.bcad"))
