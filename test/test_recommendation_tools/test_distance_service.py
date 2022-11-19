import unittest
import pandas as pd
import os
import pandas_utility as pd_util

from main.recommendation_tools.distance_service import DistanceService, DISTANCE

TEST_DISTANCE_DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../resources/simple_distance_set.csv")


class TestDistanceService(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = pd.read_csv(TEST_DISTANCE_DATASET_PATH)
        self.service = DistanceService(self.dataset)

    def test_missing_input(self):
        def get_closest_to_invalid():
            self.service.get_closest_to({"x": 5, "y": 12})

        self.assertRaises(ValueError, get_closest_to_invalid)

    def test_get_distance_between(self):
        assert self.service.get_distance_between({"x": 0, "y": 0}, {"x": 3, "y": 4}) == 5

    def test_can_get_distance_from_point(self):
        first = self.get_by_index(min)
        last = self.get_by_index(max)
        first_user_entry = {"x": 0.1, "y": 0.05, "z": 0.03}
        second_user_entry = {"x": 0.95, "y": 0.95, "z": 0.99}
        self.assertCorrectMatch(first, first_user_entry, expected_distance=.11575836902790226)
        self.assertCorrectMatch(last, second_user_entry, expected_distance=0.07141428428542856)

    def get_by_index(self, selection_function):
        indices = self.dataset.index.values
        row = self.dataset[self.dataset.index == selection_function(indices)]
        return pd_util.get_dict_from_row(row)

    def assertCorrectMatch(self, row, user_entry, expected_distance):
        response = self.service.get_closest_to(user_entry)
        for entry in row.keys():
            assert row[entry] == response[entry]
        assert response[DISTANCE] == expected_distance
