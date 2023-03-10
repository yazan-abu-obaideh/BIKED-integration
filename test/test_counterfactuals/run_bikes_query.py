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
x = x[:2000]
y = y[:2000]
settings = DefaultProcessorSettings()
PREDICTOR = load_pickled_predictor()
minima_found = []
features_to_vary = [
    'Material=Steel', 'Material=Aluminum', 'Material=Titanium', 'BB OD', 'HT Angle', 'ST Length', 'BB Length',
    'HT Thickness']
targets = ["Sim 1 Safety Factor (Inverted)", "Model Mass Magnitude"]
number_of_variables = len(features_to_vary)


class AdaptedRegressor:
    def __init__(self):
        self.p = PREDICTOR

    def _predict(self, features):
        model_input = MultiObjectiveCounterfactualsGenerator.build_from_template(x.iloc[0].values,
                                                                                 np.reshape(features,
                                                                                            (number_of_variables, -1)),
                                                                                 modifiable_indices=[
                                                                                     x.columns.get_loc(feature)
                                                                                     for
                                                                                     feature in features_to_vary])

        def handle_materials(row: pd.Series):
            materials = [
                (row.loc[material], material) for material in
                ['Material=Steel', 'Material=Aluminum', 'Material=Titanium']
            ]
            materials.sort(key=lambda _x: _x[0])
            largest = materials[-1]
            for material in materials:
                row[material[1]] = x[material[1]].min()
            row[largest[1]] = x[largest[1]].max()

        features_dataframe = pd.DataFrame(model_input, columns=x.columns)
        features_dataframe.apply(handle_materials, axis=1)

        return self.p.predict(features_dataframe) \
            .rename(columns=settings.get_label_replacements())

    def predict(self, features):
        return self._predict(features).drop(columns=y.columns.difference(targets)).values


x: pd.DataFrame
y: pd.DataFrame

prepared_x = x.drop(columns=x.columns.difference(features_to_vary))
prepared_y = y.drop(columns=y.columns.difference(targets))

regressor = AdaptedRegressor()
problem = MultiObjectiveCounterfactualsGenerator(
    prepared_x,
    prepared_y,
    prepared_x.iloc[0:1],
    regressor,
    prepared_x.columns,
    query_y={
        "Model Mass Magnitude": (-3, 0),
        "Sim 1 Safety Factor (Inverted)": (-3, 0),
    },
    bonus_objs=[],
    constraint_functions=[],
    datatypes=[Real(bounds=(-2.5, 2.5)) for _ in range(number_of_variables)]
)

cf_set = CFSet(problem, 50, 1000, initialize_from_dataset=False)
cf_set.optimize()
num_samples = 25
cfs = cf_set.sample(num_samples,
                    avg_gower_weight=1,
                    cfc_weight=1,
                    gower_weight=1,
                    diversity_weight=0.1,
                    dtai_target=np.array([1]),
                    dtai_alpha=None,
                    dtai_beta=None,
                    include_dataset=False, num_dpp=2000)


def generate_report(counterfactuals_set: pd.DataFrame, _regressor: AdaptedRegressor):
    print("Generating report...")
    report = {}
    original_query = x.iloc[0:1]
    report["original_features"] = pd_util.get_dict_from_first_row(original_query)
    report["original_performance"] = pd_util.get_dict_from_first_row(y.iloc[0:1])
    timestamp = time.time()
    report["timestamp"] = timestamp
    report["human_readable_timestamp"] = datetime.now().__str__()
    report["generated_counterfactuals"] = {i:
        {"counterfactual": pd_util.get_dict_from_first_row(
            counterfactuals_set[i:i + 1]),
            "predictor_predictions":
                pd_util.get_dict_from_first_row(
                    _regressor._predict(counterfactuals_set[i:i + 1].values))}
        for i in range(len(counterfactuals_set))
    }
    report_filename = f"{timestamp}-report-{uuid.uuid4()}.txt"
    with open(report_filename, "w") as file:
        json.dump(report, file)
        print(f"Report generation complete! Saved to {report_filename}")


generate_report(cfs, regressor)
