import pandas as pd
from pymoo.core.variable import Real

from main.evaluation.evaluation_service import load_pickled_predictor
from main.counterfactuals.multi_objective_cfe_generator import MultiObjectiveCounterfactualsGenerator, CFSet
from main.evaluation.default_processor_settings import DefaultProcessorSettings
from main.load_data import load_augmented_framed_dataset
import numpy as np

x, y, _, _ = load_augmented_framed_dataset()
settings = DefaultProcessorSettings()
PREDICTOR = load_pickled_predictor()
minima_found = []
features_to_vary = ["BB OD", "TT OD", "HT OD"]


class AdaptedRegressor:
    def __init__(self):
        self.p = PREDICTOR

    def predict(self, features):
        model_input = MultiObjectiveCounterfactualsGenerator.build_from_template(x.iloc[0].values,
                                                                                 np.reshape(features, (3, -1)),
                                                                                 modifiable_indices=[
                                                                                     x.columns.get_loc(feature)
                                                                                     for
                                                                                     feature in features_to_vary])
        return self.p.predict(pd.DataFrame(model_input, columns=x.columns)) \
            .rename(columns=DefaultProcessorSettings().get_label_replacements()).drop(columns=
            y.columns.difference(["Model Mass Magnitude"])) \
            .values


regressor = AdaptedRegressor()

regressor.predict(np.array([[1], [3], [5]]))

x: pd.DataFrame
y: pd.DataFrame

prepared_x = x.drop(columns=x.columns.difference(features_to_vary))
prepared_y = y.drop(columns=y.columns.difference(["Model Mass Magnitude"]))

problem = MultiObjectiveCounterfactualsGenerator(
    prepared_x,
    prepared_y,
    prepared_x.iloc[0:1],
    regressor,
    prepared_x.columns,
    query_y={"Model Mass Magnitude": (0, 1.5)},
    bonus_objs=[],
    constraint_functions=[],
    datatypes=[Real(-2, 2), Real(-2, 2), Real(-2, 2)]
)

cf_set = CFSet(problem, 10, 1000, initialize_from_dataset=True)
cf_set.optimize()
num_samples = 10
cfs = cf_set.sample(num_samples, 1, 1, 1, 0.1, np.array([1,1]), include_dataset=True, num_dpp=2000)
