import unittest

import pandas as pd
import os
import pandas_utility as pd_util

from main.recommendation.recommendation_service import RecommendationService, DISTANCE
from main.recommendation.recommendation_service_settings import RecommendationSettings

TEST_DISTANCE_DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../resources/datasets/microBIKED_processed.csv")


class RecommendationServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = pd.read_csv(TEST_DISTANCE_DATASET_PATH)
        self.service = RecommendationService(self.dataset, TestBikeSettings())

    def test_get_closest_to(self):
        pass


class TestBikeSettings(RecommendationSettings):
    def __init__(self):
        self.maybe = ["Head tube upper extension2", "Seat tube extension2", "Head tube lower extension2", "Wheel width rear", "Wheel width front", "Head tube type", "BB length", "Head tube diameter", "Wheel cut", "BB diameter", "Seat tube diameter", "Top tube type", "CHAINSTAYbrdgdia1", "CHAINSTAYbrdgshift", "SEATSTAYbrdgdia1", "SEATSTAYbrdgshift", "bottle SEATTUBE0 show", "bottle DOWNTUBE0 show", "Front Fender include", "Rear Fender include", "Display RACK"]
        self.yes = ["BB textfield", "Seat tube length", "Stack", "Seat angle", "CS textfield", "FCD textfield", "Head angle", "Saddle height", "Head tube length textfield", "ERD rear", "Dropout spacing style", "BSD front", "ERD front", "BSD rear", "Fork type", "Stem kind", "Display AEROBARS", "Handlebar style", "CHAINSTAYbrdgCheck", "SEATSTAYbrdgCheck", "Display WATERBOTTLES", "BELTorCHAIN", "Number of cogs", "Number of chainrings"]

    def max_n(self) -> int:
        return 10

    def include(self) -> list:
        return self.maybe + self.yes

    def weights(self) -> dict:
        maybe_weights = {key: 1 for key in self.maybe}
        yes_weights = {key: 3 for key in self.yes}
        weights = maybe_weights
        weights.update(yes_weights)
        return weights
