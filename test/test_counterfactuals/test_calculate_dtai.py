import unittest
from main.counterfactuals.calculate_dtai import calculateDTAI


class DtaiCalculatorTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_calculate_dtai(self):
        dtai = calculateDTAI([5, 3, 1], "maximize", [6, 3, 2], [1, 1, 1], [4, 4, 4])
        self.assertAlmostEqual(0.622, dtai, places=3)
