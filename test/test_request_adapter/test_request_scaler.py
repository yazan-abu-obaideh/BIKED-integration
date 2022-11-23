import unittest

from main.load_data import load_framed_dataset
from main.request_adapter.request_scaler import RequestScaler
import os
import pandas as pd
import main.pandas_utility as pd_util

RESOURCES_FILE = os.path.join(os.path.dirname(__file__))
RELATIVE_PATH = "../../resources/all_structural_data_aug.csv"


class TestRequestScaler(unittest.TestCase):

    def setUp(self) -> None:
        self.request_scaler = RequestScaler()
        self.raw_data = pd.read_csv(os.path.join(RESOURCES_FILE, RELATIVE_PATH), index_col=0)
        self.scaled_data, _, _, self.scaler = load_framed_dataset("r", True, True, True)

    def test_identical_to_load_data_scaler(self):
        first_scaled = self.scaled_data.iloc[0].to_dict()
        input_row = self.raw_data[:1]
        assert type(input_row) is pd.DataFrame
        input_dict = pd_util.get_dict_from_row(input_row)
        assert first_scaled == self.request_scaler.scale(input_dict, self.scaler)
