import unittest

import pandas as pd

from main.counterfactuals.dtai_counterfactuals_generator import DtaiCounterfactualsGenerator
from main.processing import pandas_utility as pd_util


class DummyPredictor:
    def predict(self, data: pd.DataFrame):
        data["first_objective"] = data.apply(lambda series: series.loc["x"] ** 2 + series.loc["y"] ** 2,
                                             axis=1)
        data["second_objective"] = data.apply(lambda series: series.loc["z"] ** 3 + series.loc["y"] + series.loc["x"],
                                              axis=1)
        return data.drop(columns=data.columns.difference(["first_objective", "second_objective"]))


class DtaiCounterfactualsGeneratorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.predictor = DummyPredictor()
        self.generator = DtaiCounterfactualsGenerator()

    def test_generator(self):
        pass

    def test_dummy_predictor(self):
        prediction = self.predictor.predict(pd_util.get_row_from_dict({"x": 5, "y": 10, "z": 5}))
        print(pd_util.get_dict_from_row(prediction))
