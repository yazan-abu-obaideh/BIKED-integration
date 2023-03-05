import unittest
import main.processing.pandas_utility as pd_util
from main.counterfactuals.loss_functions import LossFunctionCalculator
import pandas as pd
import numpy as np
import os

class LossFunctionsTest(unittest.TestCase):
    def setUp(self) -> None:
        with open(os.path.join(os.path.dirname(__file__), "data.csv"), "r") as file:
            self.calculator = LossFunctionCalculator(pd.read_csv(file, index_col=0))

    def test_gower_distance_with_different_dimensions(self):
        x1 = np.array([[5, 10, 3], [5, 10, 3]])
        x2 = np.array([[6, 10, 3]])
        self.assertAlmostEqual(0.033, self.calculator.np_gower_distance(x1, x2)[0], places=3)
        self.assertAlmostEqual(0.033, self.calculator.np_gower_distance(x1, x2)[1], places=3)

    def test_to_df(self):
        array = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        dataframe = self.calculator.to_dataframe(array)
        self.assertTrue("x" in dataframe.columns.values)
        self.assertEqual(1, dataframe.loc[0].loc["x"])
        self.assertEqual((3, 3), dataframe.shape)

    def test_np_gower_distance(self):
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
                               self.calculator.np_gower_distance(x1.values, x2.values)[0],
                               places=3
                               )


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
