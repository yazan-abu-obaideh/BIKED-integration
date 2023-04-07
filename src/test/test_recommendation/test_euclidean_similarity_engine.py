from src.main.recommendation.similarity_engine_settings import EngineSettings
from src.main.recommendation.similarity_engine import EuclideanSimilarityEngine, DISTANCE
import src.main.processing.pandas_utility as pd_util
import pandas as pd
import unittest
import os

TEST_DISTANCE_DATASET_PATH = os.path.join(os.path.dirname(__file__),
                                          "../resources/simple_distance_set.csv")


class EuclideanSimilarityEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = pd.read_csv(TEST_DISTANCE_DATASET_PATH)
        self.engine = EuclideanSimilarityEngine(self.dataset, TestSettings())

    def test_empty_input(self):
        with self.assertRaises(ValueError) as context:
            self.engine.get_closest_n({}, 1)
        assert context.exception.args[0] == f"Cannot provide similar entry."

    def test_distance_with_boolean_values(self):
        actual_distance = self.engine.get_distance_between({"x": 1}, {"x": True})
        self.assertEqual(0, actual_distance)

    def test_incomplete_input(self):
        response = self.engine.get_closest_to({"x": 5, "y": 12})
        self.assertCorrectMatch(row=self.get_by_index(3), response=response,
                                expected_distance=11.704699910719626)

    def test_get_invalid_closest_n(self):
        with self.assertRaises(ValueError) as context:
            self.engine.get_closest_n({"x": 5, "y": 12}, 16)
        assert context.exception.args[0] == f"Cannot get more matches than {TestSettings().max_n()}"

    def test_order_does_not_matter(self):
        self.assertEqual(self.engine.get_distance_between({"x": 1, "y": 0}, {"y": 0, "x": 1}), 0)

    def test_get_closest_indexes(self):
        user_entry = {"x": 1, "y": 1, "z": 1}

        self.assertEqual(3, self.engine.get_closest_index_to(user_entry))

        n_indexes = self.engine.get_closest_n_indexes(user_entry, n=2)

        self.assertEqual(3, n_indexes[0])
        self.assertEqual(4, n_indexes[1])

    def test_get_closest_n(self):
        user_entry = {"x": 1, "y": 1, "z": 1}
        first_response, second_response = self.engine.get_closest_n(user_entry, n=2)
        self.assertCorrectMatch(self.get_by_index(3),
                                first_response, expected_distance=0)
        self.assertCorrectMatch(self.get_by_index(4),
                                second_response, expected_distance=0)

    def test_get_distance_between(self):
        self.assertEqual(5, self.engine.get_distance_between({"x": 0, "y": 0}, {"x": 3, "y": 4}))

    def test_get_weighted_distance_between(self):
        self.engine.settings.WEIGHTS = {"x": 10}
        expected_distance = 7.0
        actual_distance = self.engine.get_distance_between({"x": 1, "y": 1}, {"x": 3, "y": 4})
        self.assertAlmostEqual(first=expected_distance,
                               second=actual_distance,
                               places=14)

    def test_can_get_distance_from_point(self):
        first = self.get_by_index(0)
        last = self.get_by_index(3)
        first_user_entry = {"x": 0.1, "y": 0.05, "z": 0.03}
        second_user_entry = {"x": 0.95, "y": 0.95, "z": 0.99}
        self.assertCorrectMatch(first, self.engine.get_closest_to(first_user_entry),
                                expected_distance=0.11575836902790226)
        self.assertCorrectMatch(last, self.engine.get_closest_to(second_user_entry),
                                expected_distance=0.07141428428542856)

    def get_by_index(self, index):
        return pd_util.get_dict_from_first_row(self.dataset[self.dataset.index == index])

    def assertCorrectMatch(self, row, response, expected_distance):
        for entry in row:
            self.assertEqual(row[entry], response[entry])
        self.assertEqual(response[DISTANCE], expected_distance)


class TestSettings(EngineSettings):
    MAX_N = 5
    WEIGHTS = {}
    INCLUDE = ["x", "y", "z"]

    def include(self) -> list:
        return self.INCLUDE

    def weights(self) -> dict:
        return self.WEIGHTS

    def max_n(self):
        return self.MAX_N
