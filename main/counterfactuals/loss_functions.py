import numpy as np
import pandas as pd

class LossFunctionCalculator:
    def __init__(self, dataset: pd.DataFrame):
        self.dataset = dataset
        self.ranges = {}
        for column in self.dataset.columns.values:
            self.ranges[column] = self.dataset[column].max() - self.dataset[column].min()

    def np_euclidean_distance(self, designs_matrix: np.array, reference_design: np.array):
        return self.euclidean_distance(self.to_dataframe(designs_matrix), self.to_dataframe(reference_design))

    def gower_distance(self, dataframe: pd.DataFrame, reference_dataframe: pd.DataFrame):
        weighted_deltas = pd.DataFrame()
        all_columns = dataframe.columns.values
        reference_row = reference_dataframe.iloc[0]
        for column in all_columns:
            weighted_deltas[column] = dataframe[column].apply(lambda value: abs(value - reference_row.loc[column]) * 1 / self.get_ranges()[column])
        return weighted_deltas.apply(np.sum, axis=1).values * (1 / len(all_columns))

    def np_changed_features(self, designs_matrix: np.array, reference_design: np.array):
        designs_matrix, reference_design = self.to_dataframe(designs_matrix), self.to_dataframe(reference_design)
        return self.changed_features(designs_matrix, reference_design)

    def changed_features(self, designs_dataframe: pd.DataFrame, reference_dataframe: pd.DataFrame):
        changes = pd.DataFrame(columns=["changes"])
        changes["changes"] = designs_dataframe.apply(
            lambda row: np.count_nonzero(row.values - reference_dataframe.iloc[0].values), axis=1)
        return changes["changes"].values

    def np_gower_distance(self, designs_matrix: np.array, reference_design: np.array):
        return self.gower_distance(self.to_dataframe(designs_matrix), self.to_dataframe(reference_design))

    def to_dataframe(self, numpy_array: np.array):
        return pd.DataFrame(numpy_array, columns=self.dataset.columns)

    def get_ranges(self):
        return self.ranges

    def euclidean_distance(self, dataframe: pd.DataFrame, reference: pd.DataFrame):
        reference_row = reference.iloc[0]
        changes = pd.DataFrame(columns=["changes"])
        changes["changes"] = dataframe.apply(lambda row: np.linalg.norm(row - reference_row), axis=1)
        return changes["changes"].values


