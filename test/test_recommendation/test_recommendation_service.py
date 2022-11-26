import unittest
import pandas as pd
import os
import pandas_utility as pd_util

from main.recommendation.recommendation_service import RecommendationService, DISTANCE

TEST_DISTANCE_DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../resources/simple_distance_set.csv")


class RecommendationServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = pd.read_csv(TEST_DISTANCE_DATASET_PATH)
        self.service = RecommendationService(self.dataset, TestSettings())

    def test_missing_input(self):
        def get_closest_to_invalid():
            self.service.get_closest_to({"x": 5, "y": 12})

        self.assertRaises(ValueError, get_closest_to_invalid)

    def test_get_invalid_closest_n(self):
        with self.assertRaises(ValueError) as context:
            self.service.get_closest_n({}, 16)
        assert context.exception.args[0] == f"Cannot get more matches than {TestSettings.MAX_N}"

    def test_get_closest_n(self):
        user_entry = {"x": 1, "y": 1, "z": 1}
        first_response, second_response = self.service.get_closest_n(user_entry, n=2)
        self.assertCorrectMatch(self.get_by_index(3),
                                first_response, expected_distance=0)
        self.assertCorrectMatch(self.get_by_index(2),
                                second_response, expected_distance=0.4330127018922193)

    def test_get_distance_between(self):
        assert self.service.get_distance_between({"x": 0, "y": 0}, {"x": 3, "y": 4}) == 5

    def test_can_get_distance_from_point(self):
        first = self.get_by_selection_function(min)
        last = self.get_by_selection_function(max)
        first_user_entry = {"x": 0.1, "y": 0.05, "z": 0.03}
        second_user_entry = {"x": 0.95, "y": 0.95, "z": 0.99}
        self.assertCorrectMatch(first, self.service.get_closest_to(first_user_entry),
                                expected_distance=0.11575836902790226)
        self.assertCorrectMatch(last, self.service.get_closest_to(second_user_entry),
                                expected_distance=0.07141428428542856)

    def get_by_selection_function(self, selection_function):
        indices = self.dataset.index.values
        row = self.dataset[self.dataset.index == selection_function(indices)]
        return pd_util.get_dict_from_row(row)

    def get_by_index(self, index):
        return pd_util.get_dict_from_row(self.dataset[self.dataset.index == index])

    def assertCorrectMatch(self, row, response, expected_distance):
        for entry in row.keys():
            assert row[entry] == response[entry]
        assert response[DISTANCE] == expected_distance


class TestSettings:
    MAX_N = 5
