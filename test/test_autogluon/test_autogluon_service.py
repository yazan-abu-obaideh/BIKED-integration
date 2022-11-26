import os.path
import unittest

import pandas_utility as pd_util
import main.load_data as load_data
from main.autogluon_model_helpers.autogluon_service import AutogluonService
from sklearn.model_selection import train_test_split

LABELS_PATH = os.path.join(os.path.dirname(__file__), "../../resources/labels.txt")


class AutogluonServiceTest(unittest.TestCase):

    def setUp(self) -> None:
        self.x, self.y, self.result_scaler = self.prepare_x_y()
        self.service = AutogluonService(self.result_scaler)
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
                                'Sim 1 Safety Factor (Inverted)': 0.542653611374427,
                                'Sim 2 Bottom Bracket Z Disp. Magnitude': 0.0023485019730819755,
                                'Sim 3 Bottom Bracket X Rot. Magnitude': 0.0063891630717543306,
                                'Sim 3 Bottom Bracket Y Disp. Magnitude': 0.01666142336216584,
                                'Sim 3 Safety Factor (Inverted)': 0.6966032103094124}

    def test_results_can_be_unscaled_back(self):
        predictions = self.service._predict_from_row(self.x)
        r2, _, _ = self.service.get_metrics(self.result_scaler.inverse_transform(predictions),
                                            self.result_scaler.inverse_transform(self.y))
        self.assertGreater(r2, 0.97)

    def test_can_get_labels(self):
        self.assertEqual({"Sim 1 Dropout X Disp. Magnitude",
                          "Sim 1 Dropout Y Disp. Magnitude",
                          "Sim 1 Bottom Bracket X Disp. Magnitude",
                          "Sim 1 Bottom Bracket Y Disp. Magnitude",
                          "Sim 2 Bottom Bracket Z Disp. Magnitude",
                          "Sim 3 Bottom Bracket Y Disp. Magnitude",
                          "Sim 3 Bottom Bracket X Rot. Magnitude",
                          "Sim 1 Safety Factor (Inverted)",
                          "Sim 3 Safety Factor (Inverted)", "Model Mass Magnitude"},
                         set(self.service.get_labels()))

    def test_can_predict(self):
        predictions = self.service._predict_from_row(self.x)
        r2, mean_square_error, mean_absolute_error = self.service.get_metrics(predictions,
                                                                              self.y)
        self.assertGreater(r2, 0.97)
        self.assertLess(mean_square_error, 0.025)
        self.assertLess(mean_absolute_error, 0.055)

    def test_input_shape(self):
        self.assertEqual(list(self.x.columns.values), self.get_input_labels())

    def test_can_predict_singular_input(self):
        model_input = self.get_first_row(self.x)
        prediction = self.service.predict_from_row(model_input)
        assert pd_util.get_dict_from_row(model_input) == self.sample_input
        self.assertEqual(prediction,
                         self.expected_output)
        model_input_from_dict = pd_util.get_row_from_dict(self.sample_input)
        self.assertEqual(self.service.predict_from_row(model_input_from_dict),
                         self.expected_output)

    def test_cannot_predict_from_partial_singular_input(self):
        incomplete_model_input = pd_util.get_row_from_dict(
            {"Material=Steel": -1.2089779626768866, "Material=Aluminum": -0.46507861303022335,
             "Material=Titanium": 1.8379997074342262, "SSB_Include": 1.0581845284004865,
             "CSB_Include": -0.9323228669601348, "CS Length": -0.4947762070020683,
             "BB Drop": 0.19327064177679704})
        self.assertRaises(KeyError, self.service.predict_from_row,
                          incomplete_model_input)

    def first_row_index(self, dataframe):
        return dataframe.index.values[0]

    def get_first_row(self, dataframe):
        return dataframe[dataframe.index == self.first_row_index(dataframe)]

    def prepare_x_y(self):
        x_scaled, y_scaled, x_scaler, y_scaler = self.get_data()
        x_test, y_test = self.standard_split(x_scaled, y_scaled)
        return x_test, y_test, y_scaler

    def get_data(self):
        return load_data.load_augmented_framed_dataset()

    def standard_split(self, x_scaled, y_scaled):
        x_train, x_test, y_train, y_test = train_test_split(x_scaled,
                                                            y_scaled,
                                                            test_size=0.2,
                                                            random_state=1950)
        return x_test, y_test

    def get_input_labels(self):
        with open(LABELS_PATH, "r") as file:
            return [line.strip() for line in file.readlines()]
