import os.path
import unittest

from service.main.processing.scaling_filter import ScalingFilter
from service.main.evaluation.default_processor_settings import DefaultMapperSettings
from service.main.load_data import load_augmented_framed_dataset
from service.main.evaluation.evaluation_request_processor import EvaluationRequestProcessor

RESOURCE_PATH = os.path.join(os.path.dirname(__file__), "../resources/SimpleModel1.xml")


class FramedMapperTest(unittest.TestCase):
    def setUp(self) -> None:
        x, y, x_scaler, y_scaler = load_augmented_framed_dataset()
        self.service = EvaluationRequestProcessor(ScalingFilter(
            x_scaler, x.columns
        ), DefaultMapperSettings())

    def test_value_filter(self):
        self.assertFalse(self.service._value_filter(None))
        self.assertFalse(self.service._value_filter(float("inf")))
        self.assertFalse(self.service._value_filter(float("-inf")))

        self.assertTrue(self.service._value_filter("STEEL"))
        self.assertTrue(self.service._value_filter(1))
        self.assertTrue(self.service._value_filter(1.15))

    def test_key_filter(self):
        self.assertFalse(self.service._key_filter(None))
        self.assertTrue(self.service._key_filter('BB textfield'))
        self.assertFalse(self.service._key_filter("SHOULD_BE_REJECTED"))
