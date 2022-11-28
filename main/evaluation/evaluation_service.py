import pandas as pd

from main.request_adapter.request_adapter import RequestAdapter
from main.request_adapter.request_adapter_settings import RequestAdapterSettings
from main.evaluation.MultilabelPredictor import MultilabelPredictor
from main.load_data import load_augmented_framed_dataset
from main.request_adapter.scaler_wrapper import ScalerWrapper

from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import pandas_utility as pd_util
import os
import __main__

RELATIVE_MODEL_PATH = "../../resources/models/Trained Models/AutogluonModels/ag-20220911_073209/"
CONSISTENT_MODEL_PATH = os.path.join(os.path.dirname(__file__),
                                     RELATIVE_MODEL_PATH)


class EvaluationService:
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
        self.adapter = RequestAdapter(DefaultAdapterSettings())

        _, _, request_scaler, result_scaler = load_augmented_framed_dataset()
        self.result_scaler = ScalerWrapper(result_scaler)

    def _predict_from_row(self, pd_row) -> pd.DataFrame:
        return self.predictor.predict(pd_row).rename(columns=self.LABEL_REPLACEMENTS)

    def predict_from_row(self, pd_row) -> dict:
        scaled_dict = pd_util.get_dict_from_row(self._predict_from_row(pd_row))
        return self.result_scaler.unscale(scaled_dict)

    def predict_from_xml(self, bike_cad_xml) -> dict:
        bike_cad_dict = self.adapter.convert_xml(bike_cad_xml)
        row = pd_util.get_row_from_dict(bike_cad_dict)
        return self.predict_from_row(row)

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
    

class DefaultAdapterSettings(RequestAdapterSettings):
    def default_values(self) -> dict:
        return {'Material=Steel': 0, 'Material=Aluminum': 0, 'Material=Titanium': 0, 'SSB_Include': 0,
                'CSB_Include': 0, 'CS Length': 0, 'BB Drop': 0, 'Stack': 0, 'SS E': 0,
                'ST Angle': 0, 'BB OD': 0, 'TT OD': 0, 'HT OD': 0, 'DT OD': 0, 'CS OD': 0,
                'SS OD': 0, 'ST OD': 0, 'CS F': 0, 'HT LX': 0, 'ST UX': 0,
                'HT UX': 0, 'HT Angle': 0, 'HT Length': 0, 'ST Length': 0, 'BB Length': 0,
                'Dropout Offset': 0, 'SSB OD': 0, 'CSB OD': 0, 'SSB Offset': 0,
                'CSB Offset': 0, 'SS Z': 0, 'SS Thickness': 0, 'CS Thickness': 0,
                'TT Thickness': 0, 'BB Thickness': 2, 'HT Thickness': 2, 'ST Thickness': 0,
                'DT Thickness': 0, 'DT Length': 0}

    def bikeCad_to_model_map(self) -> dict:
        # noinspection SpellCheckingInspection
        return {'CS textfield': 'CS Length', 'BB textfield': 'BB Drop', 'Stack': 'Stack',
                'Head angle': 'HT Angle', 'Head tube length textfield': 'HT Length',
                'Seat stay junction0': 'SS E', 'Seat angle': 'ST Angle', 'DT Length': 'DT Length',
                'Seat tube length': 'ST Length', 'BB diameter': 'BB OD', 'ttd': 'TT OD',
                'Head tube diameter': 'HT OD', 'dtd': 'DT OD', 'csd': 'CS OD', 'ssd': 'SS OD',
                'Seat tube diameter': 'ST OD', 'Wall thickness Bottom Bracket': 'BB Thickness',
                'Wall thickness Top tube': 'TT Thickness',
                'Wall thickness Head tube': 'HT Thickness',
                'Wall thickness Down tube': 'DT Thickness',
                'Wall thickness Chain stay': 'CS Thickness',
                'Wall thickness Seat stay': 'SS Thickness',
                'Wall thickness Seat tube': 'ST Thickness',
                'BB length': 'BB Length', 'Chain stay position on BB': 'CS F',
                'SSTopZOFFSET': 'SS Z',
                'Head tube upper extension2': 'HT UX', 'Seat tube extension2': 'ST UX',
                'Head tube lower extension2': 'HT LX', 'SEATSTAYbrdgshift': 'SSB Offset',
                'CHAINSTAYbrdgshift': 'CSB Offset', 'Dropout spacing': 'Dropout Offset',
                'CHAINSTAYbrdgCheck': 'CSB_Include', 'SEATSTAYbrdgCheck': 'SSB_Include',
                'SEATSTAYbrdgdia1': 'SSB OD', 'CHAINSTAYbrdgdia1': 'CSB OD'}

    def keys_whose_presence_indicates_their_value(self) -> list:
        return ["CSB_Include", "SSB_Include"]

    def raise_exception_if_missing(self) -> list:
        return []
