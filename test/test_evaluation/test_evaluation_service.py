import os.path
import unittest

from sklearn.model_selection import train_test_split

import main.processing.pandas_utility as pd_util
from main.evaluation.evaluation_service import EvaluationService
from main.processing.scaling_filter import ScalingFilter

BIKE_PATH = os.path.join(os.path.dirname(__file__), "../resources/bikes/bike(1).xml")


class EvaluationServiceTest(unittest.TestCase):

    def setUp(self) -> None:
        self.service = EvaluationService()
        self.x, self.y, request_scaler, result_scaler = self.prepare_x_y()
        self.request_scaler = ScalingFilter(request_scaler, self.x.columns)
        self.result_scaler = ScalingFilter(result_scaler, self.y.columns)
        self.sample_input = {'Material=Steel': -1.2089779626768866, 'Material=Aluminum': -0.46507861303022335,
                             'Material=Titanium': 1.8379997074342262, 'SSB_Include': 1.0581845284004865,
                             'CSB_Include': -0.9323228669601348, 'CS Length': -0.4947762070020683,
                             'BB Drop': 0.19327064177679704, 'Stack': -0.036955840782382385,
                             'SS E': -0.4348758585162575, 'ST Angle': 1.203226228166099, 'BB OD': -0.14197615979296274,
                             'TT OD': -0.5711431568166616, 'HT OD': -0.879229453202825, 'DT OD': -0.8924125880651749,
                             'CS OD': -0.6971543225296617, 'SS OD': -0.7226114906751929, 'ST OD': -0.8962254490159303,
                             'CS F': 0.1664798679079193, 'HT LX': -0.5559202673887266, 'ST UX': -0.5875970924732736,
                             'HT UX': -0.1666775498399638, 'HT Angle': 1.5120924379123033,
                             'HT Length': 0.7032710935570091, 'ST Length': 0.980667290296069,
                             'BB Length': -0.25473226064604454, 'Dropout Offset': -0.0325700226355687,
                             'SSB OD': -2.1985552817712657, 'CSB OD': -0.279547847307574,
                             'SSB Offset': -0.09050848378506038, 'CSB Offset': 0.5823537937924539,
                             'SS Z': -0.06959536571235439, 'SS Thickness': 0.5180142556590571,
                             'CS Thickness': 1.7994950500929077, 'TT Thickness': 0.2855204217004274,
                             'BB Thickness': -0.11934492802927218, 'HT Thickness': -0.7465363724789722,
                             'ST Thickness': -0.5700521782698762, 'DT Thickness': -1.0553146425778421,
                             'DT Length': 0.10253602811555089}
        self.expected_output = {'Model Mass Magnitude': 3.189100876474357,
                                'Sim 1 Bottom Bracket X Disp. Magnitude': 0.012183772767391373,
                                'Sim 1 Bottom Bracket Y Disp. Magnitude': 0.012939156170363236,
                                'Sim 1 Dropout X Disp. Magnitude': 0.011111431121145088,
                                'Sim 1 Dropout Y Disp. Magnitude': 0.021787148423259715,
                                'Sim 2 Bottom Bracket Z Disp. Magnitude': 0.0023485019730819755,
                                'Sim 3 Bottom Bracket X Rot. Magnitude': 0.0063891630717543306,
                                'Sim 3 Bottom Bracket Y Disp. Magnitude': 0.01666142336216584,
                                'Sim 1 Safety Factor (Inverted)': 0.542653611374427,
                                'Sim 3 Safety Factor (Inverted)': 0.6966032103094124}

    def test_raises_correct_exception(self):
        with self.assertRaises(ValueError) as context:
            self.service.predict_from_xml("")
        self.assertEqual("Invalid BikeCAD file", context.exception.args[0])

    def test_is_sane(self):
        with open(BIKE_PATH, "r") as file:
            xml_as_string = file.read()

        self.assertDictAlmostEqual({'Sim 1 Dropout X Disp. Magnitude': 0.006317373031884621,
                                    'Sim 1 Dropout Y Disp. Magnitude': 0.12904948712871744,
                                    'Sim 1 Bottom Bracket X Disp. Magnitude': 0.004421147229796096,
                                    'Sim 1 Bottom Bracket Y Disp. Magnitude': 0.13356138705381396,
                                    'Sim 2 Bottom Bracket Z Disp. Magnitude': 0.014787568056570236,
                                    'Sim 3 Bottom Bracket Y Disp. Magnitude': 0.14349666332423694,
                                    'Sim 3 Bottom Bracket X Rot. Magnitude': 0.6784388296958873,
                                    'Sim 1 Safety Factor (Inverted)': 467.74263810696385,
                                    'Sim 3 Safety Factor (Inverted)': 558.2490643908037,
                                    'Model Mass Magnitude': 7.403376048347106},
                                   self.service.predict_from_xml(xml_as_string))

    def test_can_predict_from_partial_dict(self):
        partial_request = {'Material=Titanium': 1.8379997074342262, 'SSB_Include': 1.0581845284004865,
                           'CSB_Include': -0.9323228669601348, 'CS Length': -0.4947762070020683,
                           'BB Drop': 0.19327064177679704}
        self.assertIsNotNone(self.service.predict_from_dict(partial_request))

    def test_cannot_predict_from_partial_row(self):
        incomplete_model_input = pd_util.get_one_row_dataframe_from_dict(
            {"Material=Steel": -1.2089779626768866, "Material=Aluminum": -0.46507861303022335,
             "Material=Titanium": 1.8379997074342262, "SSB_Include": 1.0581845284004865,
             "CSB_Include": -0.9323228669601348, "CS Length": -0.4947762070020683,
             "BB Drop": 0.19327064177679704})
        self.assertRaises(KeyError, self.service.predict_from_row,
                          incomplete_model_input)

    def test_model_and_scalers_loaded(self):
        predictions = self.service._predict_from_row(self.x)
        self.assert_correct_metrics(predictions, self.y)
        self.assert_correct_metrics(self.result_scaler.scaler.inverse_transform(predictions),
                                    self.result_scaler.scaler.inverse_transform(self.y))

    def test_order_does_not_matter(self):
        input_in_different_order = {key: self.sample_input[key]
                                    for key in sorted(self.sample_input.keys())}
        self.assertEqual(self.service.predict_from_dict(self.sample_input),
                         self.service.predict_from_dict(input_in_different_order))

    def assert_correct_metrics(self, predictions, actual):
        r2, mean_square_error, mean_absolute_error = self.service.get_metrics(predictions,
                                                                              actual)
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
