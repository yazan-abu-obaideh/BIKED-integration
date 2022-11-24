import os.path
import unittest

import pandas_utility as pd_util
import main.load_data as load_data
from main.autogluon_model_helpers.autogluon_service import AutogluonService
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd

LABELS_PATH = os.path.join(os.path.dirname(__file__), "../../resources/labels.txt")


class AutogluonServiceTest(unittest.TestCase):

    def setUp(self) -> None:
        self.service = AutogluonService()
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
        self.x, self.y, self.y_scaler = self.prepare_x_y()
        self.expected_output = {'Model Mass': -0.9461116790771484,
                                'Sim 1 Bottom Bracket X Disp.': 0.02232583984732628,
                                'Sim 1 Bottom Bracket Y Disp.': 0.2731778919696808,
                                'Sim 1 Dropout X Disp.': 0.09372919797897339,
                                'Sim 1 Dropout Y Disp.': 0.1128099337220192,
                                'Sim 1 Safety Factor': -0.8752062320709229,
                                'Sim 2 Bottom Bracket Z Disp.': 1.7482761144638062,
                                'Sim 3 Bottom Bracket X Rot.': 2.0954513549804688,
                                'Sim 3 Bottom Bracket Y Disp.': 3.2179315090179443,
                                'Sim 3 Safety Factor': -0.3395128548145294}
        self.expected_unscaled_output = self.get_unscaled_output(self.expected_output)

    def test_results_are_unscaled_back(self):
        print(self.expected_unscaled_output)
        assert False

    def test_can_get_labels(self):
        self.assertEqual(self.service.get_labels(), ["Sim 1 Dropout X Disp.", "Sim 1 Dropout Y Disp.",
                                                     "Sim 1 Bottom Bracket X Disp.", "Sim 1 Bottom Bracket Y Disp.",
                                                     "Sim 2 Bottom Bracket Z Disp.", "Sim 3 Bottom Bracket Y Disp.",
                                                     "Sim 3 Bottom Bracket X Rot.", "Sim 1 Safety Factor",
                                                     "Sim 3 Safety Factor", "Model Mass"])

    def test_can_predict(self):
        predictions = self.service.predict_from_row(self.x)
        r2, mean_square_error, mean_absolute_error = self.service.get_metrics(predictions, self.y)
        self.assertGreater(r2, 0.97)
        self.assertLess(mean_square_error, 0.025)
        self.assertLess(mean_absolute_error, 0.055)

    def test_input_shape(self):
        self.assertEqual(list(self.x.columns.values), self.get_input_labels())

    def test_can_predict_singular_input(self):
        model_input = self.get_first_row(self.x)
        prediction = self.service.predict_from_row(model_input)
        assert pd_util.get_dict_from_row(model_input) == self.sample_input
        self.assertEqual(pd_util.get_dict_from_row(prediction),
                         self.expected_output)
        model_input_from_dict = pd_util.get_row_from_dict(self.sample_input)
        self.assertEqual(pd_util.get_dict_from_row(self.service.predict_from_row(model_input_from_dict)),
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
        x_scaled, y, _, xscaler = self.get_data()
        y = self.filter_y(y)
        x_scaled = x_scaled.loc[y.index]
        y_scaled, y_scaler = self.standard_scaling(y)
        x_test, y_test = self.standard_split(x_scaled, y_scaled)
        return x_test, y_test, y_scaler

    def filter_y(self, y):
        q = y.quantile(.95)
        for col in y.columns:
            y = y[y[col] <= q[col]]
        return y

    def get_unscaled_output(self, scaled_dict):
        self.y_scaler: StandardScaler()
        scaled_row = pd_util.get_row_from_dict(scaled_dict)
        unscaled_values = self.y_scaler.inverse_transform(scaled_row)
        unscaled_row = pd.DataFrame(unscaled_values, columns=scaled_row.columns, index=scaled_row.index)
        return pd_util.get_dict_from_row(unscaled_row)

    def get_data(self):
        return load_data.load_framed_dataset("r", onehot=True, scaled=True, augmented=True)

    def standard_split(self, x_scaled, y_scaled):
        x_train, x_test, y_train, y_test = train_test_split(x_scaled,
                                                            y_scaled,
                                                            test_size=0.2,
                                                            random_state=1950)
        return x_test, y_test

    def standard_scaling(self, data):
        data_scaler = StandardScaler()
        data_scaler.fit(data)
        data_scaled = data_scaler.transform(data)
        data_scaled = pd.DataFrame(data_scaled, columns=data.columns, index=data.index)
        return data_scaled, data_scaler

    def get_input_labels(self):
        with open(LABELS_PATH, "r") as file:
            return [line.strip() for line in file.readlines()]
