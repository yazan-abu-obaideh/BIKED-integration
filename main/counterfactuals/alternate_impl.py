import os

from main.counterfactuals.loss_functions import LossFunctionCalculator

os.environ["TOKENIZERS_PARALLELISM"] = "TRUE"
import pandas as pd
import pymoo
from pymoo.core.problem import Problem, ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
import importlib
import numpy as np
from tqdm import trange, tqdm
import matplotlib.pyplot as plt
import datetime
import dill
import warnings
import glob
import textwrap
import imageio
import tensorflow as tf
import load_data

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
from main.load_data import load_augmented_framed_dataset

x_scaled, y, _, xscaler = load_data.load_augmented_framed_dataset()


class Optimization(Problem):

    def __init__(self,
                 n_variables,
                 upper_bounds,
                 lower_bounds,
                 predictor,
                 validity_fns,
                 user_query,
                 counterfactual_targets,
                 query_weight,
                 cfc_weight,
                 gower_weight):
        super().__init__(n_var=n_variables, n_obj=num_objs + 2, n_constr=len(validity_fns), xl=lower_bounds,
                         xu=upper_bounds)
        self.query = user_query
        self.target = counterfactual_targets
        self.query_weight = query_weight  # query proximity weight
        self.cfc_weight = cfc_weight  # changed features loss weight
        self.gower_weight = gower_weight  # changed features loss weight
        self.predictor = predictor
        self.validity_fns = validity_fns
        self.query = user_query
        self.loss_function_calculator = LossFunctionCalculator(
            pd.DataFrame([upper_bounds - lower_bounds], columns=[_ for _ in range(n_variables)])
        )
        assert (query_weight >= 0)
        assert (cfc_weight >= 0)

    def calculate_scores(self, x):
        all_scores = np.zeros((len(x), num_objs + 2))
        # the first n columns are the model predictions
        all_scores[:, :num_objs] = self.predictor(x)
        # n + 1 is gower distance
        all_scores[:, num_objs] = self.gower_dist(x)
        # n + 2 is changed features
        all_scores[:, num_objs + 1] = self.changed_features(x)
        all_scores[:, num_objs + 2] = self.evaluate_design(x)
        return all_scores, self.get_validity(x)

    def get_validity(self, x):
        g = np.zeros((len(x), len(self.validity_fns)))
        for i in range(len(self.validity_fns)):
            g[:, i] = self.validity_fns[i](x).flatten()
        return g

    def gower_dist(self, x):
        return self.loss_function_calculator.np_gower_distance(x, self.query.values)  # TODO

    def changed_features(self, x):
        return np.count_nonzero(x - self.query)  # TODO

    def _evaluate(self, x, out, *args, **kwargs):
        score, validity = self.calculate_scores(x)
        out["F"] = score
        out["G"] = validity

    def evaluate_design(self, x):
        # TODO: use self.counterfactual_targets to evaluate design
        return np.linalg.norm(x - self.target)


n_var = len(x_scaled.columns)
ub = np.quantile(x_scaled.values, 0.99, axis=0)
lb = np.quantile(x_scaled.values, 0.01, axis=0)
query = x_scaled.sample(1, axis=0)

from main.evaluation.evaluation_service import load_pickled_predictor

bike_predictor = load_pickled_predictor()
objectives_min = {"Model Mass Magnitude": 4,
                  "Sim 1 Dropout X Disp. Magnitude": 0.01
                  }
objectives_max = {}

obj_indexes = []

for key in objectives_min:
    obj_indexes.append(y.columns.get_loc(key))
print(obj_indexes)


def predictor_fn(x, obj_idxs=obj_indexes):
    obj_idxs = np.array(obj_idxs)
    return x[:, obj_idxs]


num_objs = len(obj_indexes)
cf_target = y.sample(1, axis=0).iloc[:, obj_indexes]
problem = Optimization(n_var, ub, lb, predictor_fn, [], query, cf_target, 1, 1, 1)
algorithm = NSGA2(pop_size=100, eliminate_duplicates=True)
res = minimize(problem, algorithm,
               ('n_gen', 100),
               seed=2,
               verbose=True)

print(res)
