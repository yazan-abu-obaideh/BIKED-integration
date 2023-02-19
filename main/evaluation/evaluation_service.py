import __main__

import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

import main.processing.pandas_utility as pd_util
from main.evaluation.default_processor_settings import DefaultProcessorSettings
from main.evaluation.MultilabelPredictor import MultilabelPredictor
from main.evaluation.Predictor import Predictor
from main.evaluation.request_processor import RequestProcessor
from main.evaluation.request_processor_settings import RequestProcessorSettings
from main.load_data import load_augmented_framed_dataset
from main.processing.bikeCad_xml_handler import BikeCadXmlHandler
from main.processing.scaling_filter import ScalingFilter
from main.resource_paths import MODEL_PATH

SCALED_MEAN = 0



def prepare_pickle():
    # TODO: investigate why this needs to be done and what it implies
    __main__.MultilabelPredictor = MultilabelPredictor


def load_pickled_predictor():
    prepare_pickle()
    return MultilabelPredictor.load(MODEL_PATH)


DEFAULT_PREDICTOR = load_pickled_predictor()




class EvaluationService:

    def __init__(self, predictor: Predictor = DEFAULT_PREDICTOR,
                 settings : RequestProcessorSettings = DefaultProcessorSettings()):
        self.predictor = predictor
        self.adapter = RequestProcessor(settings)
        x, y, input_scaler, output_scaler = self.get_data()
        self.xml_handler = BikeCadXmlHandler()
        self.request_scaler = ScalingFilter(input_scaler, x.columns)
        self.response_scaler = ScalingFilter(output_scaler, y.columns)

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
        scaled_dict = self.default_to_mean(scaled_dict)
        row = pd_util.get_row_from_dict(scaled_dict)
        return self.predict_from_row(row)

    def default_to_mean(self, bike_cad_dict):
        defaulted_keys = self.get_empty_keys(bike_cad_dict)
        for key in defaulted_keys:
            bike_cad_dict[key] = SCALED_MEAN
        return bike_cad_dict

    def get_empty_keys(self, bike_cad_dict):
        return (key for key in self.adapter.settings.get_expected_input_keys() if key not in bike_cad_dict)

    def predict_from_row(self, pd_row: pd.DataFrame) -> dict:
        predictions_row = self._predict_from_row(pd_row)
        scaled_result = pd_util.get_dict_from_row(predictions_row)
        scaled_result = self.replace_labels(scaled_result)
        unscaled_result = self.response_scaler.unscale(scaled_result)
        return self.ensure_magnitude(unscaled_result)

    def replace_labels(self, scaled_result):
        scaled_result = {self.adapter.settings.get_label_replacements().get(key, key): value
                         for key, value in
                         scaled_result.items()}
        return scaled_result

    def _predict_from_row(self, pd_row: pd.DataFrame) -> pd.DataFrame:
        return self.predictor.predict(pd_row)

    def ensure_magnitude(self, scaled_result):
        return {key: abs(value) for key, value in scaled_result.items()}

    def get_metrics(self, predictions, y_test):
        r2 = r2_score(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        return r2, mse, mae

    def get_data(self):
        return load_augmented_framed_dataset()
