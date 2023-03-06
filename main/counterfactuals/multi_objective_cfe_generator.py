import numpy as np
import pandas as pd
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize


class MultiObjectiveCounterfactualsGenerator(Problem):
    def _evaluate(self, x, out, *args, **kwargs):
        pass

    def __init__(self,
                 features_dataset: pd.DataFrame,
                 predictions_dataset: pd.DataFrame,
                 features_to_vary: list,
                 targeted_predictions: list,
                 validity_functions: list,
                 upper_bounds: np.array,
                 lower_bounds: np.array):
        self.validate_parameters(features_dataset, features_to_vary, lower_bounds, predictions_dataset,
                                 targeted_predictions, upper_bounds)
        super().__init__(n_var=len(features_to_vary),
                         n_obj=len(targeted_predictions) + 3,
                         n_constr=len(validity_functions),
                         xl=lower_bounds,
                         xu=upper_bounds)
        self.features_dataset = features_dataset
        self.ranges = self.build_ranges(features_dataset, features_to_vary)

    @staticmethod
    def build_ranges(features_dataset: pd.DataFrame, features_to_vary: list):
        subset = features_dataset.drop(columns=features_dataset.columns.difference(features_to_vary))
        return subset.max() - subset.min()

    def validate_parameters(self, features_dataset, features_to_vary, lower_bounds, predictions_dataset,
                            targeted_predictions, upper_bounds):
        self.validate_datasets(features_dataset, predictions_dataset)
        self.validate_features_to_vary(features_dataset, features_to_vary)
        self.validate_targeted_predictions(predictions_dataset, targeted_predictions)
        self.validate_bounds(features_to_vary, upper_bounds, lower_bounds)

    def np_euclidean_distance(self, designs_matrix: np.array, reference_design: np.array):
        n_columns = reference_design.shape[1]
        return self.euclidean_distance(self.alt_to_dataframe(designs_matrix, n_columns),
                                       self.alt_to_dataframe(reference_design, n_columns))

    def gower_distance(self, dataframe: pd.DataFrame, reference_dataframe: pd.DataFrame):
        weighted_deltas = pd.DataFrame()
        all_columns = dataframe.columns.values
        reference_row = reference_dataframe.iloc[0]
        list_ranges = list(self.ranges)
        for i in range(len(all_columns)):
            column = all_columns[i]
            weighted_deltas[column] = dataframe[column] \
                .apply(lambda value: abs(value - reference_row.loc[column]) * 1 / list_ranges[i])
        return weighted_deltas.apply(np.sum, axis=1).values * (1 / len(all_columns))

    def np_changed_features(self, designs_matrix: np.array, reference_design: np.array):
        designs_matrix, reference_design = self.to_dataframe(designs_matrix), self.to_dataframe(reference_design)
        return self.changed_features(designs_matrix, reference_design)

    def changed_features(self, designs_dataframe: pd.DataFrame, reference_dataframe: pd.DataFrame):
        changes = designs_dataframe.apply(
            lambda row: np.count_nonzero(row.values - reference_dataframe.iloc[0].values), axis=1)
        return changes.values

    def np_gower_distance(self, designs_matrix: np.array, reference_design: np.array):
        return self.gower_distance(self.to_dataframe(designs_matrix), self.to_dataframe(reference_design))

    def alt_to_dataframe(self, matrix: np.array, number_of_columns: int):
        return pd.DataFrame(matrix, columns=[_ for _ in range(number_of_columns)])

    def to_dataframe(self, numpy_array: np.array):
        dummy_columns = [_ for _ in range(numpy_array.shape[1])]
        return pd.DataFrame(numpy_array, columns=dummy_columns)

    def get_ranges(self):
        return self.ranges

    def euclidean_distance(self, dataframe: pd.DataFrame, reference: pd.DataFrame):
        reference_row = reference.iloc[0]
        changes = dataframe.apply(lambda row: np.linalg.norm(row - reference_row), axis=1)
        return changes.values

    def build_from_template(self, template_array, new_values, modifiable_indices):
        base = np.array([template_array for _ in range(new_values.shape[1])])
        for i in range(len(modifiable_indices)):
            base[:, modifiable_indices[i]] = new_values[i, :]
        return base

    def validate_features_to_vary(self, features_dataset: pd.DataFrame, features_to_vary: list):
        self._validate_labels(features_dataset, features_to_vary, "User has not provided any features to vary")

    def _validate_labels(self, dataset: pd.DataFrame, labels: list,
                         no_labels_message):
        assert len(labels) > 0, no_labels_message
        valid_labels = dataset.columns.values
        for label in labels:
            assert label in valid_labels, f"Expected label {label} to be in dataset {valid_labels}"

    def validate_targeted_predictions(self, predictions_dataset: pd.DataFrame, targeted_predictions: list):
        self._validate_labels(predictions_dataset,
                              targeted_predictions,
                              "User has not provided any performance targets")

    def validate_bounds(self, features_to_vary: list, upper_bounds: np.array, lower_bounds: np.array):
        valid_length = len(features_to_vary)
        assert upper_bounds.shape == (valid_length,)
        assert lower_bounds.shape == (valid_length,)

    def validate_datasets(self, features_dataset: pd.DataFrame, predictions_dataset: pd.DataFrame):
        assert len(features_dataset) == len(predictions_dataset), "Dimensional mismatch between provided datasets"
