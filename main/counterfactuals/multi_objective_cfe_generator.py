import numpy as np
import pandas as pd
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

from main.evaluation.Predictor import Predictor


class MultiObjectiveCounterfactualsGenerator(Problem):
    def __init__(self,
                 features_dataset: pd.DataFrame,
                 predictions_dataset: pd.DataFrame,
                 query_x: pd.DataFrame,
                 # target_design: pd.DataFrame,  <-What is this?

                 predictor,
                 features_to_vary: list,
                 query_y: dict,
                 bonus_objs: list,
                 constraint_functions: list,
                 upper_bounds: np.array,
                 lower_bounds: np.array):
        self.validate_parameters(features_dataset, features_to_vary, lower_bounds, predictions_dataset, upper_bounds,
                                 bonus_objs, query_y)
        self.number_of_objectives = len(predictions_dataset.columns) + 3
        self.predictor = predictor
        self.query_x = query_x
        # self.target_design = target_design
        self.bonus_objs = bonus_objs
        self.query_constraints, self.query_lb, self.query_ub = self.sort_query_y(query_y)
        self.constraint_functions = constraint_functions
        super().__init__(n_var=len(features_to_vary),
                         n_obj=self.number_of_objectives,
                         n_constr=len(constraint_functions) + len(self.query_constraints),
                         xl=lower_bounds,
                         xu=upper_bounds)
        self.features_dataset = features_dataset
        self.predictions_dataset = predictions_dataset
        self.ranges = self.build_ranges(features_dataset, features_to_vary)

    def _evaluate(self, x, out, *args, **kwargs):
        score, validity = self.calculate_scores(x)
        out["F"] = score
        out["G"] = validity

    def calculate_scores(self, x):
        all_scores = np.zeros((len(x), self.number_of_objectives))
        # the first n columns are the model predictions
        # TODO: feed x into the build_from_template method

        prediction = pd.DataFrame(self.predictor.predict(x), columns=self.predictions_dataset.columns)
        # self.predictor.predict(pd.DataFrame(x, columns=self.features_dataset.columns))\
        # .drop(columns=self.features_dataset.columns.difference(self.query_y)).values

        all_scores[:, :-3] = prediction
        # n + 1 is gower distance
        all_scores[:, -3] = self.np_gower_distance(x, self.query_x.values)
        # n + 2 is changed features
        all_scores[:, -2] = self.np_changed_features(x, self.query_x.values)
        # all_scores[:, -1] = self.np_euclidean_distance(prediction, self.target_design)
        all_scores[:, -1] = self.np_avg_gower_distance(x, self.query_x.values)
        return all_scores, self.get_constraint_satisfaction(x, prediction)

    def get_constraint_satisfaction(self, x, y):
        n_cf = len(self.constraint_functions)
        g = np.zeros((len(x), n_cf + len(self.query_constraints)))
        for i in range(n_cf):
            g[:, i] = self.constraint_functions[i](x).flatten()
        pred_consts = y.loc[:, self.query_constraints].values
        indiv_satisfaction = np.logical_and(np.less(pred_consts, self.query_ub), np.greater(pred_consts, self.query_lb))
        g[:, n_cf:] = indiv_satisfaction
        return g

    @staticmethod
    def build_ranges(features_dataset: pd.DataFrame, features_to_vary: list):
        subset = features_dataset.drop(columns=features_dataset.columns.difference(features_to_vary))
        return subset.max() - subset.min()

    def sort_query_y(self, query_y: dict):
        query_constraints = []
        query_lb = []
        query_ub = []
        for key in query_y.keys():
            query_constraints.append(key)
            query_lb.append(query_y[key][0])
            query_ub.append(query_y[key][1])
        return query_constraints, np.array(query_lb), np.array(query_ub)

    def validate_parameters(self, features_dataset, features_to_vary, lower_bounds, predictions_dataset,
                            upper_bounds, bonus_objs, query_y):
        self.validate_datasets(features_dataset, predictions_dataset)
        self.validate_features_to_vary(features_dataset, features_to_vary)
        self.validate_query_y(predictions_dataset, query_y)
        self.validate_bonus_objs(predictions_dataset, query_y)
        self.validate_bounds(features_to_vary, upper_bounds, lower_bounds)

    def np_euclidean_distance(self, designs_matrix: np.array, reference_design: np.array):
        n_columns = reference_design.shape[1]
        return self.euclidean_distance(self.alt_to_dataframe(designs_matrix, n_columns),
                                       self.alt_to_dataframe(reference_design, n_columns))

    def np_avg_gower_distance(self, designs_matrix: np.array, reference_design: np.array):
        return np.zeros(len(designs_matrix))  # TODO

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

    def validate_query_y(self, predictions_dataset: pd.DataFrame, query_y: dict):
        self._validate_labels(predictions_dataset,
                              query_y.keys(),
                              "User has not provided any performance targets")

    def validate_bonus_objs(self, predictions_dataset: pd.DataFrame, bonus_objs: list):
        self._validate_labels(predictions_dataset,
                              bonus_objs,
                              "User has not provided any performance targets")

    def validate_bounds(self, features_to_vary: list, upper_bounds: np.array, lower_bounds: np.array):
        valid_length = len(features_to_vary)
        assert upper_bounds.shape == (valid_length,)
        assert lower_bounds.shape == (valid_length,)

    def validate_datasets(self, features_dataset: pd.DataFrame, predictions_dataset: pd.DataFrame):
        assert len(features_dataset) == len(predictions_dataset), "Dimensional mismatch between provided datasets"
