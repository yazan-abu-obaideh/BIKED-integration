import numpy as np
import pandas as pd
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.core.population import Population
from pymoo.core.evaluator import Evaluator
import main.counterfactuals.calculate_dtai as calculate_dtai
import main.counterfactuals.DPPsampling as DPPsampling
# from main.evaluation.Predictor import Predictor


class CFSet: #For calling the optimization and sampling counterfactuals
    def __init__(self, problem, n_gen, pop_size, seed=None, initialize_from_dataset=True, verbose=True):
        self.problem = problem
        self.n_gen = n_gen
        self.pop_size = pop_size
        self.initialize_from_dataset = initialize_from_dataset
        self.verbose = verbose
        if seed:
            self.seed = seed
        else:
            self.seed = np.random.randint(1000000)
    def optimize(self): #Run the GA
        if self.initialize_from_dataset:
            self.generate_dataset_pop()
            print(f"Initial population initialized from dataset of {len(self.problem.features_dataset.index)} samples!")
            algorithm = NSGA2(pop_size=self.pop_size, sampling = self.pop, eliminate_duplicates=True, save_history=True)
        else:
            algorithm = NSGA2(pop_size=self.pop_size, eliminate_duplicates=True, save_history=True)
        self.res = minimize(self.problem, algorithm,
               ('n_gen', self.n_gen),
               seed=self.seed,
               verbose=True)
    def sample(self, num_samples: int, avg_gower_weight, cfc_weight, gower_weight, diversity_weight, dtai_target, dtai_alpha=None, dtai_beta=None, include_dataset=True, num_dpp = 1000): #Query from pareto front
        assert self.res, "You must call optimize before calling generate!"
        assert num_samples>0, "You must sample at least 1 counterfactual!"
        # print(self.res.X)
        # print(self.res.F)
        if self.verbose:
            print("Collecting all counterfactual candidates!")
        if include_dataset:
            self.generate_dataset_pop()
            all_cfs = self.pop
        else:
            all_cfs = Population()
        for algorithm in self.res.history:
            all_cfs = Population.merge(all_cfs, algorithm.off)

        all_cf_x, all_cf_y = self.filter_by_validity(all_cfs)
        #TODO: Filter by G (Validity)
        if len(all_cf_x)<num_samples:
            print(f"No valid counterfactuals! Returning empty dataframe.")
            return self.build_res_df(all_cf_x)

        if len(all_cf_x)<num_samples:
            print(f"Only found {len(all_cf_y)} valid counterfactuals! Returning all {len(all_cf_y)}.")
            return self.build_res_df(all_cf_x)

        if self.verbose:
            print("Scoring all counterfactual candidates!")

        if not dtai_alpha:
            dtai_alpha = np.ones_like(dtai_target)
        if not dtai_beta:
            dtai_beta = np.ones_like(dtai_target)*4
        print(all_cf_y)
        dtai_scores = calculate_dtai.calculateDTAI(all_cf_y[:,:-3], "minimize", dtai_target, dtai_alpha, dtai_beta)
        print(dtai_scores)
        cf_quality = all_cf_y[:,-3] * gower_weight + all_cf_y[:,-2] * cfc_weight  + all_cf_y[:,-1] * avg_gower_weight
        print(cf_quality)
        agg_scores = 1-dtai_scores + cf_quality
        print(agg_scores)
        if num_samples==1:
            best_idx = np.argmin(agg_scores)
            return self.build_res_df(all_cf_x[0, :])
        else:
            if len(agg_scores)>num_dpp:
                index = np.argpartition(agg_scores, -num_dpp)[-num_dpp:]
            else:
                index = range(len(agg_scores))
            samples_index = self.diverse_sample(all_cf_x[index], agg_scores[index], num_samples, diversity_weight)
            return self.build_res_df(all_cf_x[samples_index, :])

    def filter_by_validity(self, all_cfs):
        all_cf_y = all_cfs.get("F")
        all_cf_v = all_cfs.get("G")
        all_cf_x = all_cfs.get("X")

        valid = np.all(all_cf_v, axis=1)
        return all_cf_x[valid], all_cf_y[valid]

    def min2max(self, x, eps=1e-7): #Converts minimization objective to maximization, assumes rough scale~ 1
        return np.divide(np.mean(x), x+eps)


    def build_res_df(self, x):
        print("Done!")
        return pd.DataFrame(x, columns = self.problem.features_dataset.columns)
    def generate_dataset_pop(self):
        try: #Evaluate Pop if not done already
            self.pop
        except:
            x = self.problem.features_dataset.values
            mask = np.all(np.logical_and(np.greater(x, self.problem.lower_bounds), np.less(x, self.problem.upper_bounds)), axis=1)
            x = x[mask]
            pop = Population.new("X", x)
            Evaluator().eval(self.problem, pop, datasetflag = True)
            self.pop = pop
    def diverse_sample(self, x, y, num_samples, diversity_weight, eps=1e-7):
        if self.verbose:
            print("Calculating diversity matrix!")
        y = np.power(self.min2max(y), 1/diversity_weight)
        print(y)
        matrix = self.L2_vectorized(x, x)
        weighted_matrix = np.einsum('ij,i,j->ij', matrix, y, y)
        if self.verbose:
            print("Sampling diverse set of counterfactual candidates!")
        samples_index = DPPsampling.kDPPGreedySample(weighted_matrix, num_samples)
        return samples_index


    def L2_vectorized(self, X, Y):
        #Vectorize L2 calculation using x^2+y^2-2xy
        X_sq = np.sum(np.square(X), axis=1)
        Y_sq = np.sum(np.square(Y), axis=1)
        sq = np.add(np.expand_dims(X_sq, axis=-1), np.transpose(Y_sq)) - 2*np.matmul(X,np.transpose(Y))
        sq = np.clip(sq, 0.0, 1e12)
        return np.sqrt(sq)


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
        self.validate_parameters(features_dataset, features_to_vary, lower_bounds, predictions_dataset, upper_bounds, bonus_objs, query_y)
        self.number_of_objectives = len(bonus_objs) + 3
        self.x_dimension = len(features_dataset.columns)
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
        self.upper_bounds = upper_bounds
        self.lower_bounds = lower_bounds

    def _evaluate(self, x, out, *args, **kwargs):
        if "usedatasetflag" in kwargs.keys():
            datasetflag = kwargs.keys("datasetflag")
        else:
            datasetflag = False
        score, validity = self.calculate_scores(x, datasetflag)
        out["F"] = score
        out["G"] = validity

    def calculate_scores(self, x, datasetflag):
        all_scores = np.zeros((len(x), self.number_of_objectives))
        # the first n columns are the model predictions
        # TODO: feed x into the build_from_template method
        if datasetflag:
            prediction = self.predictions_dataset.copy()
        else:
            prediction = pd.DataFrame(self.predictor.predict(x), columns=self.predictions_dataset.columns)
        # self.predictor.predict(pd.DataFrame(x, columns=self.features_dataset.columns))\
            # .drop(columns=self.features_dataset.columns.difference(self.query_y)).values

        all_scores[:, :-3] = prediction.loc[:,self.bonus_objs]
        # n + 1 is gower distance
        all_scores[:, -3] = self.np_gower_distance(x, self.query_x.values)
        print(x)
        print(self.query_x.values)
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
        n_columns = reference_design.shape[1]
        return self.avg_gower_distance(self.alt_to_dataframe(designs_matrix, n_columns),
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
        return changes.values/self.x_dimension

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

    def avg_gower_distance(self, param, param1):
        pass