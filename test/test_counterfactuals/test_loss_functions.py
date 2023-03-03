import unittest
import main.processing.pandas_utility as pd_util
from main.counterfactuals.loss_functions import LossFunctionCalculator
import pandas as pd
import os

class LossFunctionsTest(unittest.TestCase):
    def setUp(self) -> None:
        with open(os.path.join(os.path.dirname(__file__), "data.csv"), "r") as file:
            self.calculator = LossFunctionCalculator(pd.read_csv(file))

    def test_gower_distance(self):
        x1 = pd_util.get_row_from_dict({
            "x": 5,
            "y": 10,
            "z": 3
        })
        x2 = pd_util.get_row_from_dict({
            "x": 6,
            "y": 10,
            "z": 3
        })
        self.assertAlmostEqual(0.033,
                               self.calculator.gower_distance(x1, x2)[0],
                               places=3
                               )
