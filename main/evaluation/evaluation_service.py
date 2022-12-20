from typing import List

from main.request_processing.request_adapter_settings import RequestAdapterSettings
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from main.evaluation.MultilabelPredictor import MultilabelPredictor
from main.request_processing.request_adapter import RequestAdapter
from main.request_processing.scaler_wrapper import ScalerWrapper
from main.load_data import load_augmented_framed_dataset
from main.xml_handler import XmlHandler
import main.pandas_utility as pd_util
import pandas as pd
import __main__
import os

SCALED_MEAN = 0

RELATIVE_MODEL_PATH = "../../resources/models/Trained Models/AutogluonModels/ag-20220911_073209/"
CONSISTENT_MODEL_PATH = os.path.join(os.path.dirname(__file__),
                                     RELATIVE_MODEL_PATH)

labels_inverted = ["Sim 1 Safety Factor",
                   "Sim 3 Safety Factor"]
labels_magnitude = ['Sim 1 Dropout X Disp.', 'Sim 1 Dropout Y Disp.', 'Sim 1 Bottom Bracket X Disp.',
                    'Sim 1 Bottom Bracket Y Disp.', 'Sim 2 Bottom Bracket Z Disp.', 'Sim 3 Bottom Bracket Y Disp.',
                    'Sim 3 Bottom Bracket X Rot.', 'Model Mass']

LABEL_REPLACEMENTS = {label: label + " (Inverted)" for label in labels_inverted}
LABEL_REPLACEMENTS.update({label: label + " Magnitude" for label in labels_magnitude})


class EvaluationService:

    def __init__(self):
        # TODO: investigate why this needs to be done and what it implies
        __main__.MultilabelPredictor = MultilabelPredictor

        self.predictor = MultilabelPredictor.load(os.path.abspath(CONSISTENT_MODEL_PATH))
        self.adapter = RequestAdapter(DefaultAdapterSettings())

        x, y, input_scaler, output_scaler = self.get_data()
        self.xml_handler = XmlHandler()
        self.request_scaler = ScalerWrapper(input_scaler, x.columns)
        self.response_scaler = ScalerWrapper(output_scaler, y.columns)

    def predict_from_xml(self, bike_cad_xml: str) -> dict:
        self.xml_handler.set_xml(bike_cad_xml)
        entries = self.xml_handler.get_entries_dict()
        self.raise_if_empty_dict(entries)
        return self.predict_from_dict(self.adapter.convert_dict(entries))

    def raise_if_empty_dict(self, bikeCad_file_entries):
        if len(bikeCad_file_entries) == 0:
            raise ValueError('Invalid BikeCAD file')

    def predict_from_dict(self, bike_cad_dict: dict) -> dict:
        scaled_dict = self.request_scaler.scale(bike_cad_dict)
        self.set_defaulted_values_to_scaled_mean(scaled_dict)
        row = pd_util.get_row_from_dict(scaled_dict)
        return self.predict_from_row(row)

    def set_defaulted_values_to_scaled_mean(self, bike_cad_dict):
        defaulted_keys = self.get_defaulted_keys(bike_cad_dict)
        for key in defaulted_keys:
            bike_cad_dict[key] = SCALED_MEAN

    def get_defaulted_keys(self, bike_cad_dict):
        return (key for key in self.adapter.settings.default_values().keys() if key not in bike_cad_dict)

    def predict_from_row(self, pd_row: pd.DataFrame) -> dict:
        scaled_result = pd_util.get_dict_from_row(self._predict_from_row(pd_row))
        scaled_result = {LABEL_REPLACEMENTS.get(key, key): value for key, value in scaled_result.items()}
        return self.ensure_magnitude(self.response_scaler.unscale(scaled_result))

    def _predict_from_row(self, pd_row: pd.DataFrame) -> pd.DataFrame:
        return self.predictor.predict(pd_row)

    def ensure_magnitude(self, scaled_result):
        return {key: abs(value) for key, value in scaled_result.items()}

    def get_metrics(self, predictions, y_test):
        r2 = r2_score(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        return r2, mse, mae

    def get_labels(self):
        labels = list(self.predictor.labels.values)
        for key, value in LABEL_REPLACEMENTS.items():
            labels.remove(key)
            labels.append(value)
        return labels

    def get_data(self):
        return load_augmented_framed_dataset()


class DefaultAdapterSettings(RequestAdapterSettings):
    def default_values(self) -> dict:
        # warn users when the supplied bikecad file has no materials field OR whenever the material vlaue is not
        # in steel, alum, titanium
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
                'Seat stay junction': 'SS E', 'Seat angle': 'ST Angle', 'DT Length': 'DT Length',
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

    def keys_whose_presence_indicates_their_value(self) -> List[str]:
        return ["CSB_Include", "SSB_Include"]

    def raise_exception_if_missing(self) -> List[str]:
        return []

    def millimeters_to_meters(self):
        return ['CS Length', 'BB Drop', 'Stack', 'SS E', 'BB OD', 'TT OD', 'HT OD', 'DT OD',
                'CS OD', 'SS OD', 'ST OD', 'CS F', 'HT LX', 'ST UX', 'HT UX', 'HT Length',
                'ST Length', 'BB Length', 'Dropout Offset', 'SSB OD', 'CSB OD', 'SSB Offset',
                'CSB Offset', 'SS Z', 'SS Thickness', 'CS Thickness', 'TT Thickness',
                'BB Thickness', 'HT Thickness', 'ST Thickness', 'DT Thickness', 'DT Length']
