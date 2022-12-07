import numpy

from main.recommendation.bike_recommendation_service import BikeRecommendationService
import unittest
import os

VALID_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../resources/bikes/FullModel1.xml")


class RecommendationServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = BikeRecommendationService()

    def test_get_closest_to(self):
        with open(VALID_MODEL_PATH, "r") as file:
            response = self.service.recommend_bike(file.read())
            print(response[0])
            array = numpy.array(list(response[1].values()))
            print(numpy.unique(array))
