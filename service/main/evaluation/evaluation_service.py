import __main__

import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

import service.main.processing.pandas_utility as pd_util
from service.main.evaluation.model_response_processor import ModelResponseProcessor
from service.main.evaluation.MultilabelPredictor import MultilabelPredictor
from service.main.evaluation.Predictor import Predictor
from service.main.evaluation.default_processor_settings import DefaultMapperSettings
from service.main.evaluation.evaluation_request_processor import EvaluationRequestProcessor
from service.main.evaluation.request_processor_settings import RequestProcessorSettings
from service.main.load_data import load_augmented_framed_dataset
from service.main.processing.scaling_filter import ScalingFilter
from service_resources.resource_paths import MODEL_PATH


def prepare_pickle():
    # TODO: investigate why this needs to be done and what it implies
    __main__.MultilabelPredictor = MultilabelPredictor


def load_pickled_predictor():
    prepare_pickle()
    return MultilabelPredictor.load(MODEL_PATH)


DEFAULT_PREDICTOR = load_pickled_predictor()


class EvaluationService:

    def __init__(self, predictor: Predictor = DEFAULT_PREDICTOR,
                 settings: RequestProcessorSettings = DefaultMapperSettings()):
        self._predictor = predictor
        x, y, input_scaler, output_scaler = self._get_data()
        request_scaler = ScalingFilter(input_scaler, x.columns)
        response_scaler = ScalingFilter(output_scaler, y.columns)
        self._request_processor = EvaluationRequestProcessor(request_scaler, settings)
        self._response_processor = ModelResponseProcessor(response_scaler)

    def evaluate_xml(self, xml_user_request: str) -> dict:
        model_input = self._request_processor.map_to_validated_model_input(xml_user_request)
        return self._evaluate(model_input)

    def _evaluate_parsed_dict(self, bike_cad_dict: dict) -> dict:
        model_input = self._request_processor.map_dict_to_validated_model_input(bike_cad_dict)
        return self._evaluate(model_input)

    def _evaluate(self, model_input):
        model_output = self._wrapped_call_predictor(model_input)
        return self._response_processor.map_to_validated_response(model_output)

    def _wrapped_call_predictor(self, request: dict) -> dict:
        predictions_dictionary = self._call_predictor(pd_util.get_single_row_dataframe_from(request))
        return pd_util.get_dict_from_first_row(predictions_dictionary)

    def _call_predictor(self, pd_row: pd.DataFrame) -> pd.DataFrame:
        return self._predictor.predict(pd_row)

    def get_metrics(self, predictions, y_test):
        r2 = r2_score(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        return r2, mse, mae

    def _get_data(self):
        return load_augmented_framed_dataset()
