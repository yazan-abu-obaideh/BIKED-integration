import unittest
import pandas as pd
import os

from main.recommendation_tools.distance_service import DistanceService

TEST_DISTANCE_DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../resources/simple_distance_set.csv")


class TestDistanceService(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = pd.read_csv(TEST_DISTANCE_DATASET_PATH)
        self.service = DistanceService(self.dataset)

    def test_can_get_distance_from_point(self):
        first = self.get_by_index(min)
        last = self.get_by_index(max)
        first_user_entry = {"x": 0.1, "y": 0.05, "z": 0.03}
        second_user_entry = {"x": 0.95, "y": 0.95, "z": 0.99}
        self.assertCorrectMatch(first, first_user_entry)
        self.assertCorrectMatch(last, second_user_entry)

    def get_by_index(self, selection_function):
        indices = self.dataset.index.values
        row = self.dataset[self.dataset.index == selection_function(indices)]
        return row

    def assertCorrectMatch(self, row, user_entry):
        assert (row.values == self.service.get_closest_to(user_entry).values).all().all()
