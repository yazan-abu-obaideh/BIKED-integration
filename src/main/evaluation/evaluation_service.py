import __main__

import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

import src.main.processing.pandas_utility as pd_util
from src.main.processing.request_validator import RequestValidator
from src.main.evaluation.default_processor_settings import DefaultProcessorSettings
from src.main.evaluation.MultilabelPredictor import MultilabelPredictor
from src.main.evaluation.Predictor import Predictor
from src.main.evaluation.request_processor import RequestProcessor
from src.main.evaluation.request_processor_settings import RequestProcessorSettings
from src.main.load_data import load_augmented_framed_dataset
from src.main.processing.bike_xml_handler import BikeXmlHandler
from src.main.processing.scaling_filter import ScalingFilter
from service_resources.resource_paths import MODEL_PATH

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
                 settings: RequestProcessorSettings = DefaultProcessorSettings()):
        self.predictor = predictor
        self.adapter = RequestProcessor(settings)
        x, y, input_scaler, output_scaler = self.get_data()
        self.xml_handler = BikeXmlHandler()
        self.request_scaler = ScalingFilter(input_scaler, x.columns)
        self.response_scaler = ScalingFilter(output_scaler, y.columns)
        self.request_validator = RequestValidator()

    def predict_from_xml(self, xml_user_request: str) -> dict:
        self.xml_handler.set_xml(xml_user_request)
        user_request = self.xml_handler.get_entries_dict()
        self.request_validator.throw_if_empty(user_request, 'Invalid BikeCAD file')
        return self.predict_from_dict(self.adapter.convert_dict(user_request))

    def predict_from_dict(self, bike_cad_dict: dict) -> dict:
        scaled_dict = self.request_scaler.scale(bike_cad_dict)
        scaled_dict = self.default_to_mean(scaled_dict)
        one_row_dataframe = pd_util.get_one_row_dataframe_from_dict(scaled_dict)
        return self.predict_from_row(one_row_dataframe)

    def default_to_mean(self, bike_cad_dict):
        defaulted_keys = self.get_empty_keys(bike_cad_dict)
        for key in defaulted_keys:
            bike_cad_dict[key] = SCALED_MEAN
        return bike_cad_dict

    def get_empty_keys(self, bike_cad_dict):
        return (key for key in self.adapter.settings.get_expected_input_keys() if key not in bike_cad_dict)

    def predict_from_row(self, pd_row: pd.DataFrame) -> dict:
        predictions_row = self._predict_from_row(pd_row)
        scaled_result = pd_util.get_dict_from_first_row(predictions_row)
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
