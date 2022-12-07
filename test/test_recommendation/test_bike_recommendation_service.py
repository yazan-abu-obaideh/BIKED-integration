import unittest

import pandas as pd
import os
import pandas_utility as pd_util

from main.recommendation.recommendation_service import RecommendationService, DISTANCE
from main.recommendation.recommendation_service_settings import RecommendationSettings

TEST_DISTANCE_DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../resources/test-assets/simple_distance_set.csv")


class RecommendationServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = pd.read_csv(TEST_DISTANCE_DATASET_PATH)
        self.service = RecommendationService(self.dataset, TestBikeSettings())

    def test_missing_input(self):
        def get_closest_to_invalid():
            self.service.get_closest_to({"x": 5, "y": 12})

        self.assertRaises(ValueError, get_closest_to_invalid)

    def test_get_invalid_closest_n(self):
        with self.assertRaises(ValueError) as context:
            self.service.get_closest_n({}, 16)
        assert context.exception.args[0] == f"Cannot get more matches than {TestBikeSettings().max_n()}"

    def test_order_does_not_matter(self):
        self.assertEqual(self.service.get_distance_between({"x": 1, "y": 0}, {"y": 0, "x": 1}), 0)

    def test_get_closest_n(self):
        user_entry = {"x": 1, "y": 1, "z": 1}
        first_response, second_response = self.service.get_closest_n(user_entry, n=2)
        self.assertCorrectMatch(self.get_by_index(3),
                                first_response, expected_distance=0)
        self.assertCorrectMatch(self.get_by_index(2),
                                second_response, expected_distance=0.4330127018922193)

    def test_get_distance_between(self):
        self.assertEqual(5, self.service.get_distance_between({"x": 0, "y": 0}, {"x": 3, "y": 4}))

    def test_get_weighted_distance_between(self):
        self.service.settings.WEIGHTS = {"x": 10}
        self.assertAlmostEqual(self.service.get_distance_between({"x": 1, "y": 1}, {"x": 3, "y": 4}), 7, places=6)


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
            self.assertEqual(row[entry], response[entry])
        self.assertEqual(response[DISTANCE], expected_distance)


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
