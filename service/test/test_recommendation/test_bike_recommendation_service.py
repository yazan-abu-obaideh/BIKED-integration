from service.main.recommendation.bike_recommendation_service import BikeRecommendationService
from service.main.processing.bike_xml_handler import BikeXmlHandler
import unittest
import os

VALID_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../resources/bikes/1310591065335.bcad")


class RecommendationServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = BikeRecommendationService()
        self.xml_handler = BikeXmlHandler()

    def test_key_filter(self):
        self.assertFalse(self.service._key_filter("SHOULD_BE_REJECTED"))
        self.assertTrue(self.service._key_filter("BB textfield"))

    def test_value_filter(self):
        self.assertFalse(self.service._value_filter(None))
        self.assertFalse(self.service._value_filter("NOT_FLOAT_OR_INT"))
        self.assertFalse(self.service._value_filter(float("inf")))
        self.assertFalse(self.service._value_filter(float("-inf")))

        self.assertTrue(self.service._value_filter(0))
        self.assertTrue(self.service._value_filter(1))
        self.assertTrue(self.service._value_filter(1.15))

    def test_get_closest_to(self):
        class TesterService(BikeRecommendationService):
            def __init__(self):
                super().__init__()
                self.key_filter_calls = 0
                self.value_filter_calls = 0

            def _key_filter(self, value):
                self.key_filter_calls += 1
                return super()._key_filter(value)

            def _value_filter(self, value):
                self.value_filter_calls += 1
                return super()._value_filter(value)

        bike_in_request = self.grab_bike_xml()
        service = TesterService()
        recommended_bike = service.recommend_bike_from_xml(bike_in_request).get("similarBikes")[0]
        self.assertEqual("http://bcd.bikecad.ca/1310591065335.bcad", recommended_bike)
        self.assertEqual(3563, service.key_filter_calls)
        self.assertEqual(31, service.value_filter_calls)

    def test_empty_request(self):
        with self.assertRaises(ValueError) as context:
            self.service.recommend_bike_from_xml("")
        self.assertEqual("Invalid BikeCAD file", context.exception.args[0])

    def grab_bike_xml(self):
        with open(VALID_MODEL_PATH, 'r') as file:
            return file.read()

    def test_buildlink(self):
        self.assertEqual("http://bcd.bikecad.ca/1.bcad", self.service._build_link("1.bcad"))
