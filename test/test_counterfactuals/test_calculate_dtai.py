import unittest
from main.counterfactuals.calculate_dtai import calculateDTAI
import numpy as np


class DtaiCalculatorTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_calculate_dtai(self):
        dtai = calculateDTAI(np.array([5, 3, 1]), "maximize", np.array([6, 3, 2]), np.array([1, 1, 1]),
                             np.array([4, 4, 4]))
        self.assertAlmostEqual(0.622, dtai, places=3)
