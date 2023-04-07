import __main__

import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

import src.main.processing.pandas_utility as pd_util
from service_resources.resource_paths import MODEL_PATH
from src.main.evaluation.MultilabelPredictor import MultilabelPredictor
from src.main.evaluation.Predictor import Predictor
from src.main.evaluation.default_processor_settings import DefaultMapperSettings
from src.main.evaluation.evaluation_request_processor import EvaluationRequestProcessor
from src.main.evaluation.request_processor_settings import RequestProcessorSettings
from src.main.load_data import load_augmented_framed_dataset
from src.main.processing.processing_pipeline import ProcessingPipeline
from src.main.processing.request_validator import RequestValidator
from src.main.processing.scaling_filter import ScalingFilter


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
        _request_scaler = ScalingFilter(input_scaler, x.columns)
        self._response_scaler = ScalingFilter(output_scaler, y.columns)
        self._request_processor = EvaluationRequestProcessor(_request_scaler, settings)
        self._request_validator = RequestValidator()
        self._model_input_to_validated_response_pipeline = ProcessingPipeline(steps=[
            self._wrapped_call_predictor,
            self._response_scaler.unscale,
            self._ensure_magnitude
        ])

    def evaluate_xml(self, xml_user_request: str) -> dict:
        model_input = self._request_processor.map_to_validated_model_input(xml_user_request)
        return self._model_input_to_validated_response_pipeline.process(model_input)

    def _evaluate_parsed_dict(self, bike_cad_dict: dict) -> dict:
        model_input = self._request_processor.map_dict_to_validated_model_input(bike_cad_dict)
        return self._model_input_to_validated_response_pipeline.process(model_input)

    def _predict_from_row(self, pd_row: pd.DataFrame) -> dict:
        predictions_row = self._call_predictor(pd_row)
        scaled_result = pd_util.get_dict_from_first_row(predictions_row)
        unscaled_result = self._response_scaler.unscale(scaled_result)
        return self._ensure_magnitude(unscaled_result)

    def _wrapped_call_predictor(self, request: dict) -> dict:
        predictions_dictionary = self._call_predictor(pd_util.get_single_row_dataframe_from(request))
        return pd_util.get_dict_from_first_row(predictions_dictionary)

    def _call_predictor(self, pd_row: pd.DataFrame) -> pd.DataFrame:
        return self._predictor.predict(pd_row)

    def _ensure_magnitude(self, scaled_result):
        return {key: abs(value) for key, value in scaled_result.items()}

    def get_metrics(self, predictions, y_test):
        r2 = r2_score(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        return r2, mse, mae

    def _get_data(self):
        return load_augmented_framed_dataset()
