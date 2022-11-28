import unittest

from main.load_data import load_augmented_framed_dataset, one_hot_encode_material
from main.request_adapter.scaler_wrapper import ScalerWrapper
import os
import pandas as pd
import main.pandas_utility as pd_util

RESOURCES_FILE = os.path.join(os.path.dirname(__file__))
RELATIVE_PATH = "../../resources/all_structural_data_aug.csv"


class TestScalerWrapper(unittest.TestCase):

    def setUp(self) -> None:
        self.raw_data = pd.read_csv(os.path.join(RESOURCES_FILE, RELATIVE_PATH), index_col=0)
        # x, y, x_scaler, y_scaler
        self.scaled_data, _, scaler, _ = load_augmented_framed_dataset()
        self.request_scaler = ScalerWrapper(scaler)
        self.input_row = self.prepare_input_row()
        self.first_scaled = self.scaled_data.iloc[0].to_dict()

    def test_identical_to_load_data_scaler(self):
        assert type(self.input_row) is pd.DataFrame
        input_dict = pd_util.get_dict_from_row(self.input_row)
        assert self.first_scaled == self.request_scaler.scale(input_dict)

    def test_order_does_not_matter(self):
        something = {'Material=Steel': 0.8271449363608141, 'Material=Aluminum': -0.46507861303022335,
                     'Material=Titanium': -0.5440697275169644, 'SSB_Include': -0.9450147617557437,
                     'CSB_Include': -0.9323228669601348, 'CS Length': 0.41901291964455895,
                     'BB Drop': 0.6850895496264587,
                     'Stack': -0.03724471292440881, 'SS E': -0.4348758585162575, 'ST Angle': -0.24738407840999618,
                     'BB OD': -0.14197615979296274, 'TT OD': 0.3377870558504079, 'HT OD': 0.05902675085116946,
                     'DT OD': -0.05902677854744301, 'CS OD': -0.258128668383897, 'SS OD': -0.529499443375879,
                     'ST OD': 0.364699608145729, 'CS F': 0.1664798679079193, 'HT LX': 0.2072952115978548,
                     'ST UX': -0.6210800676191586, 'HT UX': 0.847940833513158, 'HT Angle': 0.40434937789177955,
                     'HT Length': -0.0016687264182314615, 'ST Length': 0.933827449129208,
                     'BB Length': -0.25473226064604454,
                     'Dropout Offset': -0.15605860475685474, 'SSB OD': 0.7197781475562169, 'CSB OD': 0.7466269916241078,
                     'SSB Offset': -0.09050848378506038, 'CSB Offset': 0.5823537937924539, 'SS Z': -1.8822858666926465,
                     'SS Thickness': 0.947655814847033, 'CS Thickness': -0.7146337378156017,
                     'TT Thickness': -0.48600996909073707,
                     'BB Thickness': -0.8350274604180904, 'HT Thickness': 0.6610529908788535,
                     'ST Thickness': -0.4744145107322768,
                     'DT Thickness': -0.8176505921283834, 'DT Length': 0.4384846712626987}
        first_unscaled = self.request_scaler.unscale(something)
        print(first_unscaled)
        some_other_thing = {'SSB_Include': -0.9450147617557437,
                            'CSB_Include': -0.9323228669601348, 'CS Length': 0.41901291964455895,
                            'BB Drop': 0.6850895496264587,
                            'Stack': -0.03724471292440881, 'SS E': -0.4348758585162575,
                            'ST Angle': -0.24738407840999618,
                            'BB OD': -0.14197615979296274, 'TT OD': 0.3377870558504079, 'HT OD': 0.05902675085116946,
                            'DT OD': -0.05902677854744301, 'CS OD': -0.258128668383897, 'SS OD': -0.529499443375879,
                            'ST OD': 0.364699608145729, 'CS F': 0.1664798679079193, 'HT LX': 0.2072952115978548,
                            'ST UX': -0.6210800676191586, 'HT UX': 0.847940833513158, 'HT Angle': 0.40434937789177955,
                            'HT Length': -0.0016687264182314615, 'ST Length': 0.933827449129208,
                            'BB Length': -0.25473226064604454,
                            'Dropout Offset': -0.15605860475685474, 'SSB OD': 0.7197781475562169,
                            'CSB OD': 0.7466269916241078,
                            'SSB Offset': -0.09050848378506038, 'CSB Offset': 0.5823537937924539,
                            'SS Z': -1.8822858666926465,
                            'SS Thickness': 0.947655814847033, 'CS Thickness': -0.7146337378156017,
                            'TT Thickness': -0.48600996909073707,
                            'BB Thickness': -0.8350274604180904, 'HT Thickness': 0.6610529908788535,
                            'ST Thickness': -0.4744145107322768,
                            'DT Thickness': -0.8176505921283834, 'DT Length': 0.4384846712626987,
                            'Material=Steel': 0.8271449363608141, 'Material=Aluminum': -0.46507861303022335,
                            'Material=Titanium': -0.5440697275169644}
        other_unscaled = self.request_scaler.unscale(some_other_thing)
        print(other_unscaled)
        self.assertEqual(first_unscaled, other_unscaled)

    def test_unscaling_works(self):
        scaled_once = self.request_scaler.scale(pd_util.get_dict_from_row(self.input_row))
        unscaled_once = self.request_scaler.unscale(scaled_once)
        unscaled_twice = self.request_scaler.unscale(self.request_scaler.scale(unscaled_once))
        scaled_twice = self.request_scaler.scale(unscaled_twice)
        for key in self.first_scaled.keys():
            self.assertAlmostEqual(scaled_twice[key], self.first_scaled[key], 10)

    def prepare_input_row(self):
        input_row = self.raw_data[:1]
        input_row = input_row.iloc[:, :-11]
        input_row = one_hot_encode_material(input_row)
        return input_row
