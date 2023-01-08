from main.recommendation.recommendation_service_settings import RecommendationSettings
from main.recommendation.recommendation_service import RecommendationService, DISTANCE
import main.pandas_utility as pd_util
import pandas as pd
import unittest
import os



TEST_DISTANCE_DATASET_PATH = os.path.join(os.path.dirname(__file__),
                                          "../resources/simple_distance_set.csv")


class RecommendationServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = pd.read_csv(TEST_DISTANCE_DATASET_PATH)
        self.service = RecommendationService(self.dataset, TestSettings())

    def test_empty_input(self):
        with self.assertRaises(ValueError) as context:
            self.service.get_closest_n({}, 1)
        assert context.exception.args[0] == f"Cannot recommend similar bike."

    def test_incomplete_input(self):
        response = self.service.get_closest_to({"x": 5, "y": 12})
        self.assertCorrectMatch(row=self.get_by_index(3), response=response,
                                expected_distance=11.704699910719626)

    def test_get_invalid_closest_n(self):
        with self.assertRaises(ValueError) as context:
            self.service.get_closest_n({"x": 5, "y": 12}, 16)
        assert context.exception.args[0] == f"Cannot get more matches than {TestSettings().max_n()}"

    def test_order_does_not_matter(self):
        self.assertEqual(self.service.get_distance_between({"x": 1, "y": 0}, {"y": 0, "x": 1}), 0)

    def test_get_closest_n(self):
        user_entry = {"x": 1, "y": 1, "z": 1}
        first_response, second_response = self.service.get_closest_n(user_entry, n=2)
        self.assertCorrectMatch(self.get_by_index(3),
                                first_response, expected_distance=0)
        self.assertCorrectMatch(self.get_by_index(4),
                                second_response, expected_distance=0)

    def test_get_distance_between(self):
        self.assertEqual(5, self.service.get_distance_between({"x": 0, "y": 0}, {"x": 3, "y": 4}))

    def test_get_weighted_distance_between(self):
        self.service.settings.WEIGHTS = {"x": 10}
        expected_distance = 7.0
        actual_distance = self.service.get_distance_between({"x": 1, "y": 1}, {"x": 3, "y": 4})
        self.assertAlmostEqual(first=expected_distance,
                               second=actual_distance,
                               places=14)

    def test_can_get_distance_from_point(self):
        first = self.get_by_index(0)
        last = self.get_by_index(3)
        first_user_entry = {"x": 0.1, "y": 0.05, "z": 0.03}
        second_user_entry = {"x": 0.95, "y": 0.95, "z": 0.99}
        self.assertCorrectMatch(first, self.service.get_closest_to(first_user_entry),
                                expected_distance=0.11575836902790226)
        self.assertCorrectMatch(last, self.service.get_closest_to(second_user_entry),
                                expected_distance=0.07141428428542856)


    def get_by_index(self, index):
        return pd_util.get_dict_from_row(self.dataset[self.dataset.index == index])

    def assertCorrectMatch(self, row, response, expected_distance):
        for entry in row:
            self.assertEqual(row[entry], response[entry])
        self.assertEqual(response[DISTANCE], expected_distance)


class TestSettings(RecommendationSettings):
    MAX_N = 5
    WEIGHTS = {}
    INCLUDE=["x", "y", "z"]

    def include(self) -> list:
        return self.INCLUDE

    def weights(self) -> dict:
        return self.WEIGHTS

    def max_n(self):
        return self.MAX_N
