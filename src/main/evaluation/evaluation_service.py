import __main__

import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

import src.main.processing.pandas_utility as pd_util
from src.main.processing.algebraic_parser import AlgebraicParser
from src.main.processing.request_validator import RequestValidator
from src.main.evaluation.default_mapper_settings import DefaultMapperSettings
from src.main.evaluation.MultilabelPredictor import MultilabelPredictor
from src.main.evaluation.Predictor import Predictor
from src.main.evaluation.framed_mapper import FramedMapper
from src.main.evaluation.framed_mapper_settings import FramedMapperSettings
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
                 settings: FramedMapperSettings = DefaultMapperSettings()):
        self.predictor = predictor
        self.framed_mapper = FramedMapper(settings)
        x, y, input_scaler, output_scaler = self.get_data()
        self.request_scaler = ScalingFilter(input_scaler, x.columns)
        self.response_scaler = ScalingFilter(output_scaler, y.columns)
        self.request_validator = RequestValidator()
        self.parser = AlgebraicParser()

    def evaluate_xml(self, xml_user_request: str) -> dict:
        xml_handler = BikeXmlHandler()
        xml_handler.set_xml(xml_user_request)
        user_request = xml_handler.get_parsable_entries_(self.parser.attempt_parse,
                                                         key_filter=self._key_filter,
                                                         parsed_value_filter=self._value_filter)
        self.request_validator.throw_if_empty(user_request, 'Invalid BikeCAD file')
        self.request_validator.throw_if_does_not_contain(user_request, ["MATERIAL"])
        return self._evaluate_parsed_dict(user_request)

    def _evaluate_parsed_dict(self, bike_cad_dict: dict) -> dict:
        framed_dict = self.framed_mapper.map_dict(bike_cad_dict)
        scaled_dict = self.request_scaler.scale(framed_dict)
        processed_dict = self._default_to_mean(scaled_dict)
        one_row_dataframe = pd_util.get_single_row_dataframe_from(processed_dict)
        return self._predict_from_row(one_row_dataframe)

    def _default_to_mean(self, bike_cad_dict):
        defaulted_keys = self.get_empty_keys(bike_cad_dict)
        for key in defaulted_keys:
            bike_cad_dict[key] = SCALED_MEAN
        return bike_cad_dict

    def get_empty_keys(self, bike_cad_dict):
        return (key for key in self.framed_mapper.settings.get_expected_input_keys() if key not in bike_cad_dict)

    def _predict_from_row(self, pd_row: pd.DataFrame) -> dict:
        predictions_row = self._call_predictor(pd_row)
        scaled_result = pd_util.get_dict_from_first_row(predictions_row)
        scaled_result = self.replace_labels(scaled_result)
        unscaled_result = self.response_scaler.unscale(scaled_result)
        return self.ensure_magnitude(unscaled_result)

    def replace_labels(self, scaled_result):
        scaled_result = {self.framed_mapper.settings.get_label_replacements().get(key, key): value
                         for key, value in
                         scaled_result.items()}
        return scaled_result

    def _call_predictor(self, pd_row: pd.DataFrame) -> pd.DataFrame:
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

    def _key_filter(self, key):
        return key in self.framed_mapper.settings.get_expected_xml_keys()

    def _value_filter(self, parsed_value):
        return parsed_value is not None and self._valid_if_numeric(parsed_value)

    def _valid_if_numeric(self, parsed_value):
        if type(parsed_value) in [float, int]:
            return parsed_value not in [float("-inf"), float("inf")]
        return True
