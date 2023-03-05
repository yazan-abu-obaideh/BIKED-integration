import numpy as np
import pandas as pd

class LossFunctionCalculator:
    def __init__(self, dataset: pd.DataFrame):
        self.dataset = dataset
    def gower_distance(self, x1, x2):
        weighted_deltas = pd.DataFrame()
        all_columns = x1.columns.values
        for column in all_columns:
            weighted_deltas[column] = x1[column].apply(lambda value: abs(value - x2.iloc[0].loc[column]) * 1/self.get_ranges()[column])
        return weighted_deltas.apply(np.sum, axis=1).values * (1 / len(all_columns))

    def changed_features(self, x1, x2):
        x1, x2 = self.to_dataframe(x1), self.to_dataframe(x2)
        changes = pd.DataFrame(columns=["changes"])
        changes["changes"] = x1.apply(lambda row: np.count_nonzero(row.values - x2.iloc[0].values), axis=1)
        return changes["changes"].values

    def np_gower_distance(self, x1, x2):
        return self.gower_distance(self.to_dataframe(x1), self.to_dataframe(x2))

    def to_dataframe(self, x1):
        return pd.DataFrame(x1, columns=self.dataset.columns)

    def get_ranges(self):
        ranges = {}
        for column in self.dataset.columns.values:
            ranges[column] = self.dataset[column].max() - self.dataset[column].min()
        return ranges

