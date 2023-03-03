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
        self.x = x
        self.y = y
        self.predictor = predictor

    def build_explainer(self, targets):
        dtai_lambda = lambda row: self.simple_dtai(row, targets)
        self.y[DTAI] = self.y.apply(dtai_lambda, axis=1)
        design_target_index_data = self.y[DTAI]
        dice_model = dice_ml.Model(model=self.build_counterfactuals_model(self.predictor, targets), backend="sklearn",
                                   model_type=ModelTypes.Regressor)
        data_for_dice = pd.concat([self.x, design_target_index_data], axis=1)
        dice_data = dice_ml.Data(dataframe=data_for_dice,
                                 continuous_features=list(self.x.columns.values),
                                 outcome_name="dtai")
        return dice_ml.Dice(dice_data,
                            dice_model,
                            method="genetic")

    def build_counterfactuals_model(self, predictor, targets):

        dtai_lambda = lambda row: self.simple_dtai(row, targets)
        class ModelWrapper(CounterfactualsPredictor):
            def predict(self, _x):
                predictions = predictor.predict(_x)
                predictions[DTAI] = predictions.apply(dtai_lambda, axis=1)
                return predictions[DTAI].values

        return ModelWrapper()

    @staticmethod
    def simple_dtai(row, targets):
        list_generator = range(len(row))
        assert len(targets) == len(row)
        return calculateDTAI(
            row.values,
            direction="maximize",
            targets=targets,
            alpha_values=[1 for _ in list_generator],
            beta_values=[4 for _ in list_generator],
        )

    def generate_counterfactuals(self, targets, changes):
        return self.build_explainer(targets).generate_counterfactuals(self.x[0:1],
                                                               total_CFs=5,
                                                               features_to_vary=changes,
                                                               desired_range=[0.85, 1])
