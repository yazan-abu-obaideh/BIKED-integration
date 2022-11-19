from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import pandas_utility as pd_util

from main.xml_handler import XmlHandler
from main.request_adapter.request_adapter import RequestAdapter
import os
from main.autogluon_model_helpers.MultilabelPredictor import MultilabelPredictor
import __main__

RELATIVE_MODEL_PATH = "../../resources/models/Trained Models/AutogluonModels/ag-20220911_073209/"
CONSISTENT_MODEL_PATH = os.path.join(os.path.dirname(__file__),
                                     RELATIVE_MODEL_PATH)


class AutogluonService:
    def __init__(self):
        # TODO: investigate why this needs to be done
        #  and what it implies
        __main__.MultilabelPredictor = MultilabelPredictor

        self.predictor = MultilabelPredictor.load(os.path.abspath(CONSISTENT_MODEL_PATH))
        self.xml_handler = XmlHandler()
        self.adapter = RequestAdapter()

    def predict_from_row(self, pd_row):
        return self.predictor.predict(pd_row)

    def predict_from_xml(self, bike_cad_xml) -> dict:
        bike_cad_dict = self.adapter.convert_xml(bike_cad_xml)
        row = pd_util.get_row(bike_cad_dict)
        return pd_util.get_dict_from_row(self.predictor.predict(row))

    def get_metrics(self, predictions, y_test):
        r2 = r2_score(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        return r2, mse, mae

    def get_labels(self):
        return list(self.predictor.labels.values)
