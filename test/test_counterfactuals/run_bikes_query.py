import time
import uuid

import pandas as pd
from pymoo.core.variable import Real
from datetime import datetime
from main.evaluation.evaluation_service import load_pickled_predictor
from main.counterfactuals.multi_objective_cfe_generator import MultiObjectiveCounterfactualsGenerator, CFSet
from main.evaluation.default_processor_settings import DefaultProcessorSettings
from main.load_data import load_augmented_framed_dataset
import main.processing.pandas_utility as pd_util
import numpy as np
import json

x, y, _, _ = load_augmented_framed_dataset()
settings = DefaultProcessorSettings()
PREDICTOR = load_pickled_predictor()
minima_found = []
features_to_vary = ["BB OD", "TT OD", "HT OD"]


class AdaptedRegressor:
    def __init__(self):
        self.p = PREDICTOR

    def _predict(self, features):
        model_input = MultiObjectiveCounterfactualsGenerator.build_from_template(x.iloc[0].values,
                                                                                 np.reshape(features, (3, -1)),
                                                                                 modifiable_indices=[
                                                                                     x.columns.get_loc(feature)
                                                                                     for
                                                                                     feature in features_to_vary])
        return self.p.predict(pd.DataFrame(model_input, columns=x.columns)) \
            .rename(columns=DefaultProcessorSettings().get_label_replacements())

    def predict(self, features):
        return self._predict(features).drop(columns=y.columns.difference(["Model Mass Magnitude"])).values


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
    datatypes=[Real(bounds=(-2, 2)), Real(bounds=(-2, 2)), Real(bounds=(-2, 2))]
)

cf_set = CFSet(problem, 5, 500, initialize_from_dataset=True)
cf_set.optimize()
num_samples = 10
cfs = cf_set.sample(num_samples,
                    avg_gower_weight=1,
                    cfc_weight=1,
                    gower_weight=1,
                    diversity_weight=0.1,
                    dtai_target=np.array([1]),
                    dtai_alpha=np.array([1]),
                    dtai_beta=np.array([4]),
                    include_dataset=True, num_dpp=2000)


def generate_report(counterfactuals_set: pd.DataFrame, _regressor: AdaptedRegressor):
    report = {}
    original_query = x.iloc[0:1]
    report["original_features"] = pd_util.get_dict_from_row(original_query)
    report["original_performance"] = pd_util.get_dict_from_row(y.iloc[0:1])
    timestamp = time.time()
    report["timestamp"] = timestamp
    report["human_readable_timestamp"] = datetime.now().__str__()
    report["generated_counterfactuals"] = {i:
                                               {"counterfactual": pd_util.get_dict_from_row(counterfactuals_set[i:i+1]),
                                                "predictor_predictions":
                                                    pd_util.get_dict_from_row(_regressor._predict(counterfactuals_set[i:i+1].values))}
                                           for i in range(len(counterfactuals_set))
                                           }
    with open(f"{timestamp}-report-{uuid.uuid4()}.txt", "w") as file:
        json.dump(report, file)

generate_report(cfs, regressor)
