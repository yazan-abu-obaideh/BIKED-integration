import unittest
import pandas as pd
import os

from main.distance_service.distance_service import DistanceService

TEST_DISTANCE_DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../resources/simple_distance_set.csv")


class TestDistanceService(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = pd.read_csv(TEST_DISTANCE_DATASET_PATH)
        self.service = DistanceService()

    def test_dataset_loaded(self):
        self.dataset: pd.DataFrame
        print(self.dataset.index)
        print(self.dataset[self.dataset.index == 0])

    def test_can_get_distance_from_point(self):
        first = self.dataset[self.dataset.index == 0]
        assert first == self.service.get_closest_to({"x": 0, "y": 0, "z": 0})
