import numpy as np
import pandas as pd

from main.counterfactuals.multi_objective_cfe_generator import MultiObjectiveCounterfactualsGenerator
from main.evaluation.Predictor import Predictor
from main.evaluation.evaluation_service import load_pickled_predictor
from main.load_data import load_augmented_framed_dataset
from main.evaluation.default_processor_settings import DefaultProcessorSettings
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

x, y, _, _ = load_augmented_framed_dataset()
settings = DefaultProcessorSettings()
minima_found = []


class MyPredictor(Predictor):
    def __init__(self):
        self.p = load_pickled_predictor()
        self.current_minimum = float("inf")

    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        predictions = self.p.predict(data).rename(columns=settings.get_label_replacements())
        latest_minimum = predictions["Model Mass Magnitude"].min()
        if latest_minimum < self.current_minimum:
            self.current_minimum = latest_minimum
            minima_found.append(self.current_minimum)
            print(f"Minimum updated to {latest_minimum}")
        return predictions


PREDICTOR = MyPredictor()

generator = MultiObjectiveCounterfactualsGenerator(
    features_dataset=x,
    predictions_dataset=y,
    base_query=x.iloc[0:1],
    target_design=y.iloc[100:101],
    predictor=PREDICTOR,
    features_to_vary=["DT Thickness"],
    targeted_predictions=["Model Mass Magnitude"],
    validity_functions=[],
    validation_functions=[],
    upper_bounds=np.array([3 for _ in range(1)]),
    lower_bounds=np.array([-3 for _ in range(1)])
)

algorithm = NSGA2(pop_size=1000, eliminate_duplicates=True)
res = minimize(generator, algorithm,
               ('n_gen', 15),
               seed=2,
               verbose=True)

for value in res.X:
    query = x.iloc[0:1]
    print(f"Base value: {query['DT Thickness']}")
    print(f"OG result: {PREDICTOR.predict(query)['Model Mass Magnitude']}")

    query = pd.DataFrame(query.values, columns=query.columns.values)
    query["DT Thickness"] = [value]
    print(f"Modified value: {query['DT Thickness']}")
    print(f"Modified result: {PREDICTOR.predict(query)['Model Mass Magnitude']}")

