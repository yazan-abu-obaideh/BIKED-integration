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
