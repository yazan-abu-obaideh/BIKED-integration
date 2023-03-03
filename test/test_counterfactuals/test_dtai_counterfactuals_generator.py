import random
import unittest

import pandas as pd

from main.evaluation.Predictor import Predictor
from main.counterfactuals.dtai_counterfactuals_generator import DtaiCounterfactualsGenerator
from main.processing import pandas_utility as pd_util


class DummyPredictor(Predictor):
    def predict(self, data: pd.DataFrame):
        data["first_objective"] = data.apply(lambda series: series.loc["x"] ** 2 + series.loc["y"] ** 2,
                                             axis=1)
        data["second_objective"] = data.apply(lambda series: series.loc["z"] ** 3 + series.loc["y"] + series.loc["x"],
                                              axis=1)
        return data.drop(columns=data.columns.difference(["first_objective", "second_objective"]))


class DtaiCounterfactualsGeneratorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.predictor = DummyPredictor()
        x, y = self.build_data()
        self.generator = DtaiCounterfactualsGenerator(self.predictor, x, y)

    def build_data(self):
        x = pd_util.get_row_from_dict({
            "x": 0,
            "y": 0,
            "z": 0
        })
        for i in range(250):
            new = pd_util.get_row_from_dict({
                "x": i + 3,
                "y": i * 2,
                "z": (i + 2) ** 2 - 1
            })
            x = pd.concat([x, new], axis=0)
        y = self.predictor.predict(x)
        error_generator = lambda value: value + (random.random() * random.choice([-1, 1]))
        y["first_objective"] = y["first_objective"].apply(error_generator)
        y["second_objective"] = y["second_objective"].apply(error_generator)
        return x.drop(columns=["first_objective", "second_objective"]), y

    def test_build_data(self):
        x, y = self.build_data()
        print(x.head())
        print(y.head())

    def test_generator(self):
        pass

    def test_dummy_predictor(self):
        prediction = self.predictor.predict(pd_util.get_row_from_dict({"x": 5, "y": 10, "z": 5}))
        self.assertEqual(125, prediction.iloc[0].loc["first_objective"])
        self.assertEqual(140, prediction.iloc[0].loc["second_objective"])
