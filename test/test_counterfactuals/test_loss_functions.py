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

    def test_concat_numpy_arrays(self):
        template_array = np.array([1, 0, 3])
        new_values = np.array([[5, 6, 7, 10]])
        result = self.calculator.build_from_template(template_array, new_values, [1])
        self.assertEqual(4, result.shape[0])
        self.assertEqual(3, result.shape[1])
        self.assertEqual(7, result[2][1])
    def test_concat_multi_dimensional_numpy_arrays(self):
        template_array = np.array([1, 0, 3, 0])
        new_values = np.array([[5, 6, 7, 10, 12], [12, 13, 14, 15, 13]])
        result = self.calculator.build_from_template(template_array, new_values, [1, 3])
        self.assertEqual(5, result.shape[0])
        self.assertEqual(4, result.shape[1])
        self.assertEqual(12, result[0][3])



    def test_euclidean_distance(self):
        x1 = [[1, 2, 5], [2, 4, 5], [1, 3, 6]]
        reference = [[1, 1, 1]]
        design_distances = self.calculator.np_euclidean_distance(np.array(x1), np.array(reference))
        self.assertAlmostEqual(17 ** 0.5, design_distances[0], places=5)
        self.assertAlmostEqual(29 ** 0.5, design_distances[2], places=5)
        self.assertEqual(3, len(design_distances))


    def test_changed_features(self):
        x1 = [[1, 2, 5], [2, 4, 5], [1, 3, 6]]
        x2 = [[1, 3, 6]]
        changes = self.calculator.np_changed_features(np.array(x1), np.array(x2))
        self.assertEqual(2, changes[0])
        self.assertEqual(3, changes[1])
        self.assertEqual(0, changes[2])
        self.assertEqual(3, len(changes))

    def test_gower_distance_with_different_dimensions(self):
        x1 = np.array([[5, 10, 3], [5, 10, 3]])
        x2 = np.array([[6, 10, 3]])
        self.assertAlmostEqual(0.033, self.calculator.np_gower_distance(x1, x2)[0], places=3)
        self.assertAlmostEqual(0.033, self.calculator.np_gower_distance(x1, x2)[1], places=3)

    def test_to_df(self):
        array = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        dataframe = self.calculator.to_dataframe(array)
        self.assertEqual(1, dataframe.loc[0].loc[0])
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
