from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import pandas_utility as pd_util

from main.xml_handler import XmlHandler
from main.request_adapter.request_adapter import RequestAdapter
from main.request_adapter.settings import Settings
import os
from main.autogluon_model_helpers.MultilabelPredictor import MultilabelPredictor
import __main__

RELATIVE_MODEL_PATH = "../../resources/models/Trained Models/AutogluonModels/ag-20220911_073209/"
CONSISTENT_MODEL_PATH = os.path.join(os.path.dirname(__file__),
                                     RELATIVE_MODEL_PATH)


class AutogluonService:
    labels_inverted = ["Sim 1 Safety Factor", "Sim 3 Safety Factor"]
    labels_magnitude = ['Sim 1 Dropout X Disp.', 'Sim 1 Dropout Y Disp.', 'Sim 1 Bottom Bracket X Disp.',
                        'Sim 1 Bottom Bracket Y Disp.', 'Sim 2 Bottom Bracket Z Disp.', 'Sim 3 Bottom Bracket Y Disp.',
                        'Sim 3 Bottom Bracket X Rot.', 'Model Mass']

    LABEL_REPLACEMENTS = {label: label + " (Inverted)" for label in labels_inverted}
    LABEL_REPLACEMENTS.update({label: label + " Magnitude" for label in labels_magnitude})

    def __init__(self):
        # TODO: investigate why this needs to be done
        #  and what it implies
        __main__.MultilabelPredictor = MultilabelPredictor

        self.predictor = MultilabelPredictor.load(os.path.abspath(CONSISTENT_MODEL_PATH))
        self.xml_handler = XmlHandler()
        self.adapter = RequestAdapter(Settings())

    def predict_from_row(self, pd_row):
        return self.predictor.predict(pd_row).rename(columns=self.LABEL_REPLACEMENTS)

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
        unaltered_labels = list(self.predictor.labels.values)
        for key, value in self.LABEL_REPLACEMENTS.items():
            unaltered_labels.remove(key)
            unaltered_labels.append(value)
        return unaltered_labels
