import numpy as np
import pandas as pd

class LossFunctionCalculator:
    def __init__(self, dataset: pd.DataFrame):
        self.dataset = dataset
    def gower_distance(self, x1, x2):
        weighted_deltas = pd.DataFrame()
        all_columns = x1.columns.values
        for column in all_columns:
            weighted_deltas[column] = abs(x1[column] - x2[column]) * (1/self.get_ranges()[column])
        return weighted_deltas.apply(np.sum, axis=1).values * (1 / len(all_columns))

    def np_gower_distance(self, x1, x2):
        pass


    def get_ranges(self):
        ranges = {}
        for column in self.dataset.columns.values:
            ranges[column] = self.dataset[column].max() - self.dataset[column].min()
        return ranges

