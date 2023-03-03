import dice_ml
import pandas as pd
import numpy as np
from dice_ml.constants import ModelTypes
from abc import abstractmethod, ABCMeta
from main.counterfactuals.calculate_dtai import calculateDTAI
from main.evaluation.Predictor import Predictor

DTAI = 'dtai'


class CounterfactualsPredictor(metaclass=ABCMeta):
    @abstractmethod
    def predict(self, data: pd.DataFrame) -> np.array:
        pass


class DtaiCounterfactualsGenerator:

    def __init__(self,
                 predictor: Predictor,
                 x,
                 y):
        class ModelWrapper(CounterfactualsPredictor):
            def __init__(self):
                pass

            def predict(self, _x):
                predictions = predictor.predict(_x)
                predictions[DTAI] = predictions.apply(DtaiCounterfactualsGenerator.simple_dtai, axis=1)
                return predictions[DTAI].values

        self.x = x
        y[DTAI] = y.apply(self.simple_dtai, axis=1)
        design_target_index_data = y[DTAI]
        dice_model = dice_ml.Model(model=ModelWrapper(), backend="sklearn", model_type=ModelTypes.Regressor)
        data_for_dice = pd.concat([self.x, design_target_index_data], axis=1)
        dice_data = dice_ml.Data(dataframe=data_for_dice,
                                 continuous_features=list(self.x.columns.values),
                                 outcome_name="dtai")

        self.explainer = dice_ml.Dice(dice_data,
                                      dice_model,
                                      method="genetic")

    @staticmethod
    def simple_dtai(row):
        list_generator = range(len(row))
        return calculateDTAI(
            row.values,
            direction="maximize",
            targets=[1 for _ in list_generator],
            alpha_values=[1 for _ in list_generator],
            beta_values=[4 for _ in list_generator],
        )

    def generate_counterfactuals(self):
        return self.explainer.generate_counterfactuals(self.x[0:1],
                                                       total_CFs=5,
                                                       features_to_vary=[c for c in self.x.columns.values if
                                                                         c.endswith("Thickness")],
                                                       desired_range=[0.85, 1])
