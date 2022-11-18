import unittest
import pandas as pd
import os
import numpy as np

from main.recommendation_tools.distance_service import DistanceService

TEST_DISTANCE_DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../resources/simple_distance_set.csv")


class TestDistanceService(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = pd.read_csv(TEST_DISTANCE_DATASET_PATH)
        self.service = DistanceService(self.dataset)

    def test_dataset_loaded(self):
        self.dataset: pd.DataFrame
        print(self.dataset.index)
        print(self.dataset[self.dataset.index == 0])

    def test_can_get_distance_from_point(self):
        first = self.get_by_index(min)
        last = self.get_by_index(max)
        assert first.equals(self.service.get_closest_to({"x": 0.1, "y": 0.05, "z": 0.03}))
        assert last.equals(self.service.get_closest_to({"x": 0.95, "y": 0.9, "z": 0.88}))

    def get_by_index(self, fun):
        indices = self.dataset.index.values
        row = self.dataset[self.dataset.index == fun(indices)]
        return row
