import os.path
import unittest

from sklearn.model_selection import train_test_split

import src.main.processing.pandas_utility as pd_util
from src.main.evaluation.evaluation_service import EvaluationService
from src.main.processing.scaling_filter import ScalingFilter

BIKE_PATH = os.path.join(os.path.dirname(__file__), "../resources/bikes/(4800).xml")


class EvaluationServiceTest(unittest.TestCase):

    def setUp(self) -> None:
        self.service = EvaluationService()
        self.x, self.y, request_scaler, result_scaler = self.prepare_x_y()
        self.request_scaler = ScalingFilter(request_scaler, self.x.columns)
        self.result_scaler = ScalingFilter(result_scaler, self.y.columns)
        self.sample_input = {'Material=Steel': 0.8271449363608141, 'Material=Aluminum': -0.46507861303022335,
                             'Material=Titanium': -0.5440697275169644, 'SSB_Include': -0.9450147617557437,
                             'CSB_Include': -0.9323228669601348, 'CS Length': -0.35028661439732467,
                             'BB Drop': -0.1544953575549022, 'Stack': -0.0379252894111939,
                             'SS E': -0.16383852546719213, 'ST Angle': 2.36455520534093,
                             'BB OD': 1.2704546076501892, 'TT OD': -0.4170541293473518,
                             'HT OD': 0.08942680459076938, 'DT OD': -0.4570870737439202,
                             'CS OD': -0.24471155169908107, 'SS OD': -0.5298026020058619,
                             'ST OD': 0.379568476070093, 'CS F': -0.05997101198707037,
                             'HT LX': -0.22274090734521784, 'ST UX': -0.17859053297003494,
                             'HT UX': 0.7198017671343204, 'HT Angle': 1.4719711522617185,
                             'HT Length': 1.5354636604045708, 'ST Length': 0.4469654256518064,
                             'BB Length': -0.461260613117197, 'Dropout Offset': -0.7032407703632412,
                             'SSB OD': -0.26947988656276173, 'CSB OD': -0.279547847307574,
                             'SSB Offset': -0.056997290322807315, 'CSB Offset': 0.22893254089370635,
                             'SS Z': -0.46204285917458726, 'SS Thickness': 0.9214403976762411,
                             'CS Thickness': 0.2509374633376663, 'TT Thickness': -0.15479200809276833,
                             'BB Thickness': 0.49282141277749913, 'HT Thickness': 2.9026934109858655,
                             'ST Thickness': 0.23272460681845872, 'DT Thickness': 1.7696907824504056,
                             'DT Length': -0.1689535437867544}

    @unittest.skip
    def test_default_material_values(self):
        assert False

    @unittest.skip
    def test_ensure_magnitude_raises(self):
        assert False

    def test_uses_filters_and_produces_expected_response(self):
        class TesterService(EvaluationService):
            def __init__(self):
                super().__init__()
                self.value_filter_calls = 0
                self.key_filter_calls = 0

            def _key_filter(self, key):
                self.key_filter_calls += 1
                return super()._key_filter(key)

            def _value_filter(self, parsed_value):
                self.value_filter_calls += 1
                return super()._value_filter(parsed_value)

        service = TesterService()

        xml_as_string = self.get_xml()

        service_response = service.evaluate_xml(xml_as_string)
        self.assertEqual(6189, service.key_filter_calls)
        self.assertEqual(43, service.value_filter_calls)
        self.assertDictAlmostEqual({'Sim 1 Dropout X Disp. Magnitude': 0.038326118317548265,
                                    'Sim 1 Dropout Y Disp. Magnitude': 0.09414663183265932,
                                    'Sim 1 Bottom Bracket X Disp. Magnitude': 0.05474823933361474,
                                    'Sim 1 Bottom Bracket Y Disp. Magnitude': 0.05830368655186024,
                                    'Sim 2 Bottom Bracket Z Disp. Magnitude': 0.0024333662165477855,
                                    'Sim 3 Bottom Bracket Y Disp. Magnitude': 0.019052710337140566,
                                    'Sim 3 Bottom Bracket X Rot. Magnitude': 0.006138438802087421,
                                    'Sim 1 Safety Factor (Inverted)': 12.041694474674063,
                                    'Sim 3 Safety Factor (Inverted)': 3.6281390549872006,
                                    'Model Mass Magnitude': 2.6662627465729853},
                                   service_response)

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

    def test_empty_request(self):
        with self.assertRaises(ValueError) as context:
            self.service.evaluate_xml("")
        self.assertEqual("Invalid BikeCAD file", context.exception.args[0])

    def get_xml(self):
        with open(BIKE_PATH, "r") as file:
            return file.read()

    def test_can_predict_from_partial_dict(self):
        partial_request = {'Material=Titanium': 1.8379997074342262, 'SSB_Include': 1.0581845284004865,
                           'CSB_Include': -0.9323228669601348, 'CS Length': -0.4947762070020683,
                           'BB Drop': 0.19327064177679704}
        self.assertIsNotNone(self.service._evaluate_parsed_dict(partial_request))

    def test_cannot_predict_from_partial_row(self):
        incomplete_model_input = pd_util.get_single_row_dataframe_from(
            {"Material=Steel": -1.2089779626768866, "Material=Aluminum": -0.46507861303022335,
             "Material=Titanium": 1.8379997074342262, "SSB_Include": 1.0581845284004865,
             "CSB_Include": -0.9323228669601348, "CS Length": -0.4947762070020683,
             "BB Drop": 0.19327064177679704})
        self.assertRaises(KeyError, self.service._predict_from_row,
                          incomplete_model_input)

    def test_model_and_scalers_loaded(self):
        predictions = self.service._call_predictor(self.x)
        self.assert_correct_metrics(*self.service.get_metrics(predictions, self.y))
        unscaled_y = self.result_scaler.unscale_dataframe(self.y)
        unscaled_predictions = self.result_scaler.unscale_dataframe(predictions)
        r2 = self.service.get_metrics(predictions, self.y)[0]
        r2_after_scaling = self.service.get_metrics(unscaled_predictions, unscaled_y)[0]
        self.assertAlmostEqual(
            r2,
            r2_after_scaling,
            places=7
        )

    def test_order_does_not_matter(self):
        input_in_different_order = {key: self.sample_input[key]
                                    for key in sorted(self.sample_input.keys())}
        self.assertEqual(self.service._evaluate_parsed_dict(self.sample_input),
                         self.service._evaluate_parsed_dict(input_in_different_order))

    def assert_correct_metrics(self, r2, mean_square_error, mean_absolute_error):
        self.assertGreater(r2, 0.72)
        self.assertLess(mean_square_error, 0.65)
        self.assertLess(mean_absolute_error, 0.12)

    def first_row_index(self, dataframe):
        return dataframe.index[0]

    def get_first_row(self, dataframe):
        return dataframe[dataframe.index == self.first_row_index(dataframe)]

    def prepare_x_y(self):
        x_scaled, y_scaled, x_scaler, y_scaler = self.service.get_data()
        x_test, y_test = self.standard_split(x_scaled, y_scaled)
        return x_test, y_test, x_scaler, y_scaler

    def standard_split(self, x_scaled, y_scaled):
        x_train, x_test, y_train, y_test = train_test_split(x_scaled,
                                                            y_scaled,
                                                            test_size=0.2,
                                                            random_state=1950)
        return x_test, y_test

    def assertDictAlmostEqual(self, expected, actual, decimal_places=5):
        """Asserts two dictionaries containing float values are equal up to a specified precision"""
        expected_length = len(expected)
        actual_length = len(actual)
        self.assertEqual(expected_length, actual_length,
                         f"Expected dictionary with length {expected_length}, got length "
                         f"{actual_length} instead.")
        actual_keys = actual.keys()
        for key, value in expected.items():
            self.assertTrue(key in actual_keys)
            self.assertAlmostEqual(value, actual[key], places=decimal_places,
                                   msg=f"Key {key} in dictionary has unexpected value")
