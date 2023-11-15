import os.path
import unittest

from sklearn.model_selection import train_test_split

from service.main.evaluation.default_processor_settings import DefaultMapperSettings
from service.main.evaluation.evaluation_request_processor import EvaluationRequestProcessor
from service.main.evaluation.evaluation_service import EvaluationService
from service.main.processing.scaling_filter import ScalingFilter

BIKE_PATH = os.path.join(os.path.dirname(__file__), "../resources/bikes/(4800).xml")


class EvaluationServiceTest(unittest.TestCase):

    def setUp(self) -> None:
        self.service = EvaluationService()
        self.x, self.y, request_scaler, result_scaler = self.prepare_x_y()
        self.request_scaler = ScalingFilter(request_scaler, self.x.columns)
        self.result_scaler = ScalingFilter(result_scaler, self.y.columns)
        self.sample_input = {'Down tube front diameter': 29.0, 'Seat tube length': 570.0, 'Seat tube extension2': 14.3,
                             'Seat tube diameter': 29.0, 'Chain stay back diameter': 17.0, 'SSTopZOFFSET': 9.0,
                             'Head tube upper extension2': 23.3, 'CHAINSTAYbrdgshift': 350.0,
                             'Head tube length textfield': 157.3, 'Top tube front dia2': 25.4,
                             'Head angle': 73.49999999999999, 'CHAINSTAYbrdgCheck': 1.0,
                             'Wall thickness Seat tube': 0.9, 'Top tube rear dia2': 31.8,
                             'Chain stay position on BB': 15.0, 'Chain stay vertical diameter': 29.7,
                             'Head tube diameter': 32.0, 'Wall thickness Chain stay': 1.2, 'MATERIAL': 'STEEL',
                             'BB diameter': 40.0, 'Dropout spacing': 130.0, 'Stack': 565.6, 'Down tube rear dia2': 29.0,
                             'Seat angle': 73.49999999999999, 'FCD textfield': 570.0, 'CS textfield': 440.0,
                             'CHAINSTAYbrdgdia1': 18.0, 'BB length': 68.0, 'Seat stay bottom diameter': 13.0,
                             'BB textfield': 280.0, 'SEATSTAYbrdgshift': 330.0, 'Wall thickness Top tube': 0.9,
                             'SEATSTAYbrdgdia1': 16.0, 'Down tube rear diameter': 29.0, 'Top tube front diameter': 25.4,
                             'Wall thickness Seat stay': 1.0, 'SEATSTAYbrdgCheck': 1.0, 'Down tube front dia2': 29.0,
                             'Wall thickness Down tube': 0.9, 'FORK0L': 380.0, 'Head tube lower extension2': 39.5,
                             'SEATSTAY_HR': 13.0, 'Top tube rear diameter': 31.8}

    @unittest.skip
    def test_default_material_values(self):
        assert False

    def test_uses_filters_and_produces_expected_response(self):
        class TesterProcessor(EvaluationRequestProcessor):
            def __init__(self, request_scaler, settings):
                super().__init__(request_scaler, settings)
                self.value_filter_calls = 0
                self.key_filter_calls = 0

            def _key_filter(self, key):
                self.key_filter_calls += 1
                return super()._key_filter(key)

            def _value_filter(self, parsed_value):
                self.value_filter_calls += 1
                return super()._value_filter(parsed_value)

        processor = TesterProcessor(self.request_scaler, DefaultMapperSettings())
        self.service._request_processor = processor

        xml_as_string = self.get_xml()

        service_response = self.service.evaluate_xml(xml_as_string).get("evaluationScores")
        self.assertEqual(6189, processor.key_filter_calls)
        self.assertEqual(43, processor.value_filter_calls)
        self.assertDictAlmostEqual(
            {'Sim 1 Dropout X Disp.': 0.031835912456953074,
             'Sim 1 Dropout Y Disp.': -0.09439129799216761,
             'Sim 1 Bottom Bracket X Disp.': 0.047671656752443343,
             'Sim 1 Bottom Bracket Y Disp.': -0.05662733500227418,
             'Sim 2 Bottom Bracket Z Disp.': 0.0032005112380842507,
             'Sim 3 Bottom Bracket Y Disp.': -0.01831319488624808,
             'Sim 3 Bottom Bracket X Rot.': 0.007070461308021893,
             'Sim 1 Safety Factor (Inverted)': 8.524915946216408,
             'Sim 3 Safety Factor (Inverted)': 2.3434577746185496,
             'Model Mass Magnitude': 2.453795866500706},
            service_response)

    def test_empty_request(self):
        with self.assertRaises(ValueError) as context:
            self.service.evaluate_xml("")
        self.assertEqual("Invalid BikeCAD file", context.exception.args[0])

    def get_xml(self):
        with open(BIKE_PATH, "r") as file:
            return file.read()

    def test_can_handle_post_version20point1_files(self):
        class TesterProcessor(EvaluationRequestProcessor):

            def _convert_to_legacy_format(processor_self, result_dict: dict):
                legacy_format = super()._convert_to_legacy_format(result_dict)
                self.assertEqual("0.8", legacy_format["Wall thickness Top tube"])
                self.assertEqual("1.4", legacy_format["Wall thickness Bottom Bracket"])
                return legacy_format

        processor = TesterProcessor(self.request_scaler, DefaultMapperSettings())
        self.service._request_processor = processor
        with open(os.path.join(os.path.dirname(__file__), "../resources/bikes/butted(1).bcad")) as butted_file:
            result = self.service.evaluate_xml(butted_file.read())
        print(f"{result=}")

    def test_can_predict_from_partial_dict(self):
        partial_request = {'MATERIAL': "TITANIUM"}
        self.assertIsNotNone(self.service._evaluate_parsed_dict(partial_request))

    def test_cannot_predict_from_partial_row(self):
        incomplete_model_input = {"Material=Steel": -1.2089779626768866, "Material=Aluminum": -0.46507861303022335,
                                  "Material=Titanium": 1.8379997074342262, "SSB_Include": 1.0581845284004865,
                                  "CSB_Include": -0.9323228669601348, "CS Length": -0.4947762070020683,
                                  "BB Drop": 0.19327064177679704}
        self.assertRaises(KeyError, self.service._wrapped_call_predictor,
                          incomplete_model_input)

    def test_model_and_scalers_loaded(self):
        predictions = self.service._call_predictor(self.x)
        self.assert_correct_metrics(*self.service.get_metrics(self.y, predictions))
        unscaled_y = self.result_scaler.unscale_dataframe(self.y)
        unscaled_predictions = self.result_scaler.unscale_dataframe(predictions)
        r2 = self.service.get_metrics(self.y, predictions)[0]
        r2_after_scaling = self.service.get_metrics(unscaled_y, unscaled_predictions)[0]
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
        self.assertGreater(r2, 0.73)
        self.assertLess(mean_square_error, 0.65)
        self.assertLess(mean_absolute_error, 0.12)

    def first_row_index(self, dataframe):
        return dataframe.index[0]

    def get_first_row(self, dataframe):
        return dataframe[dataframe.index == self.first_row_index(dataframe)]

    def prepare_x_y(self):
        x_scaled, y_scaled, x_scaler, y_scaler = self.service._get_data()
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
