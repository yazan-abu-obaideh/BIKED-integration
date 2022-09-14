import unittest

import src.load_data as load_data
from src.MultilabelPredictor import MultilabelPredictor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import sklearn.metrics
import pandas as pd
import os
import __main__


class AutogluonLearningTest(unittest.TestCase):

    def setUp(self) -> None:
        self.sample_input = {'Material=Steel': -1.2089779626768866, 'Material=Aluminum': -0.46507861303022335,
                             'Material=Titanium': 1.8379997074342262, 'SSB_Include': 1.0581845284004865,
                             'CSB_Include': -0.9323228669601348, 'CS Length': -0.4947762070020683,
                             'BB Drop': 0.19327064177679704, 'Stack': -0.036955840782382385,
                             'SS E': -0.4348758585162575,
                             'ST Angle': 1.203226228166099, 'BB OD': -0.14197615979296274, 'TT OD': -0.5711431568166616,
                             'HT OD': -0.879229453202825, 'DT OD': -0.8924125880651749, 'CS OD': -0.6971543225296617,
                             'SS OD': -0.7226114906751929, 'ST OD': -0.8962254490159303, 'CS F': 0.1664798679079193,
                             'HT LX': -0.5559202673887266, 'ST UX': -0.5875970924732736, 'HT UX': -0.1666775498399638,
                             'HT Angle': 1.5120924379123033, 'HT Length': 0.7032710935570091,
                             'ST Length': 0.980667290296069,
                             'BB Length': -0.25473226064604454, 'Dropout Offset': -0.0325700226355687,
                             'SSB OD': -2.1985552817712657, 'CSB OD': -0.279547847307574,
                             'SSB Offset': -0.09050848378506038,
                             'CSB Offset': 0.5823537937924539, 'SS Z': -0.06959536571235439,
                             'SS Thickness': 0.5180142556590571,
                             'CS Thickness': 1.7994950500929077, 'TT Thickness': 0.2855204217004274,
                             'BB Thickness': -0.11934492802927218, 'HT Thickness': -0.7465363724789722,
                             'ST Thickness': -0.5700521782698762, 'DT Thickness': -1.0553146425778421,
                             'DT Length': 0.10253602811555089}
        self.expected_output = {'Sim 1 Dropout X Disp.': 0.09372919797897339,
                                'Sim 1 Dropout Y Disp.': 0.1128099337220192,
                                'Sim 1 Bottom Bracket X Disp.': 0.02232583984732628,
                                'Sim 1 Bottom Bracket Y Disp.': 0.2731778919696808,
                                'Sim 2 Bottom Bracket Z Disp.': 1.7482761144638062,
                                'Sim 3 Bottom Bracket Y Disp.': 3.2179315090179443,
                                'Sim 3 Bottom Bracket X Rot.': 2.0954513549804688,
                                'Sim 1 Safety Factor': -0.8752062320709229,
                                'Sim 3 Safety Factor': -0.3395128548145294,
                                'Model Mass': -0.9461116790771484}
        __main__.MultilabelPredictor = MultilabelPredictor
        relative_path = os.path.join(os.path.dirname(__file__),
                                     "../resources/models/Trained Models/AutogluonModels/ag-20220911_073209/")
        self.multi_predictor = MultilabelPredictor.load(os.path.abspath(relative_path))

    def test_can_get_labels(self):
        self.multi_predictor: MultilabelPredictor
        labels_from_predictor = list(self.multi_predictor.labels.values)
        assert labels_from_predictor == ['Sim 1 Dropout X Disp.', 'Sim 1 Dropout Y Disp.',
                                         'Sim 1 Bottom Bracket X Disp.', 'Sim 1 Bottom Bracket Y Disp.',
                                         'Sim 2 Bottom Bracket Z Disp.', 'Sim 3 Bottom Bracket Y Disp.',
                                         'Sim 3 Bottom Bracket X Rot.', 'Sim 1 Safety Factor',
                                         'Sim 3 Safety Factor', 'Model Mass']

    def test_can_predict(self):
        x_test, y_test = self.prepare_x_y()

        predictions = self.multi_predictor.predict(x_test)
        r2, mse, mae = self.get_metrics(predictions, y_test)
        print(r2, mse, mae)
        assert r2 > 0.93
        assert mse < 0.06
        assert mae < 0.11

    def test_input_shape(self):
        x, y = self.prepare_x_y()
        assert list(x.columns.values) == self.get_input_labels()

    def test_can_predict_singular_input(self):
        x, y = self.prepare_x_y()
        model_input = self.get_first_row(x)
        prediction = self.multi_predictor.predict(model_input)
        assert self.get_dict_from_row(model_input) == self.sample_input
        assert (self.get_dict_from_row(prediction)) == \
               self.expected_output
        model_input_from_dict = self.get_row_from_dict(self.sample_input)
        assert self.get_dict_from_row(self.multi_predictor.predict(model_input_from_dict)) == self.expected_output

    def test_cannot_predict_from_partial_singular_input(self):
        incomplete_model_input = self.get_row_from_dict(
            {'Material=Steel': -1.2089779626768866, 'Material=Aluminum': -0.46507861303022335,
             'Material=Titanium': 1.8379997074342262, 'SSB_Include': 1.0581845284004865,
             'CSB_Include': -0.9323228669601348, 'CS Length': -0.4947762070020683,
             'BB Drop': 0.19327064177679704})
        self.assertRaises(KeyError, self.multi_predictor.predict,
                          incomplete_model_input)

    def get_row_from_dict(self, model_input_dict):
        return pd.DataFrame([list(model_input_dict.values())], columns=list(model_input_dict.keys()))

    def get_dict_from_row(self, row):
        return row.loc[self.first_row_index(row)].to_dict()

    def first_row_index(self, dataframe):
        return dataframe.index.values[0]

    def get_first_row(self, dataframe):
        return dataframe[dataframe.index == self.first_row_index(dataframe)]

    def prepare_x_y(self):
        x_scaled, y, _, xscaler = self.get_data()
        y = self.filter_y(y)
        x_scaled = x_scaled.loc[y.index]
        y_scaled = self.standard_scaling(y)
        x_test, y_test = self.standard_split(x_scaled, y_scaled)
        return x_test, y_test

    def filter_y(self, y):
        q = y.quantile(.95)
        for col in y.columns:
            y = y[y[col] <= q[col]]
        return y

    def get_data(self):
        return load_data.load_framed_dataset("r", onehot=True, scaled=True, augmented=True)

    def standard_split(self, x_scaled, y_scaled):
        x_train, x_test, y_train, y_test = train_test_split(x_scaled, y_scaled, test_size=0.2, random_state=1950)
        return x_test, y_test

    def get_metrics(self, predictions, y_test):
        r2 = sklearn.metrics.r2_score(y_test, predictions)
        mse = sklearn.metrics.mean_squared_error(y_test, predictions)
        mae = sklearn.metrics.mean_absolute_error(y_test, predictions)
        return r2, mse, mae

    def standard_scaling(self, data):
        data_scaler = StandardScaler()
        data_scaler.fit(data)
        data_scaled = data_scaler.transform(data)
        data_scaled = pd.DataFrame(data_scaled, columns=data.columns, index=data.index)
        return data_scaled

    def get_input_labels(self):
        with open("../resources/labels.txt", "r") as file:
            return [line.strip() for line in file.readlines()]
