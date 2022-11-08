import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

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

    def get_row(self, adapted_request_dict):
        model_input_dict = {key: float(value) for key, value in adapted_request_dict.items()}
        return self.get_row_from_dict(model_input_dict)

    def get_dict_from_row(self, row):
        return row.loc[self.first_row_index(row)].to_dict()

    def first_row_index(self, dataframe):
        return dataframe.index.values[0]

    def predict_from_row(self, pd_row):
        return self.predictor.predict(pd_row)

    def predict_from_xml(self, bike_cad_xml) -> dict:
        bike_cad_dict = self.adapter.convert_xml(bike_cad_xml)
        row = self.get_row(bike_cad_dict)
        return self.get_dict_from_row(self.predictor.predict(row))

    def get_metrics(self, predictions, y_test):
        r2 = r2_score(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        return r2, mse, mae

    def get_row_from_dict(self, model_input_dict):
        return pd.DataFrame([list(model_input_dict.values())], columns=list(model_input_dict.keys()))

    def get_labels(self):
        return list(self.predictor.labels.values)
