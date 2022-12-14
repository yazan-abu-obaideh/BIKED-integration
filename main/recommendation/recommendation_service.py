import pandas as pd
import numpy as np
import main.pandas_utility as pd_util
from main.recommendation.recommendation_service_settings import RecommendationSettings
from main.request_processing.scaler_wrapper import ScalerWrapper

DISTANCE = 'distance_from_user_entry'


class RecommendationService:
    def __init__(self, data, settings:RecommendationSettings):
        self.data = data
        # TODO: USE the sheet provided
        self.settings = settings

        # TODO: make it so the distance service remains completely agnostic of the type of data,
        #  the settings, the scaling and unscaling required - because this service CAN be concrete.
        #  Do this right and you won't have to change anything about this package if the dataset changes.

    def calculate_distances(self, user_entry_dict: dict):
        self.data: pd.DataFrame
        filtered_user_entry = {key: value for key, value in user_entry_dict.items() if key in self.settings.include()}
        user_entry_row = pd.Series(filtered_user_entry)

        def distance_from_user_entry(row):
            return self.get_distance_between(user_entry_row, row)

        self.data[DISTANCE] = self.data.apply(distance_from_user_entry, axis=1)


    def get_distance_between(self, reference_entry, second_entry):
        try:
            deltas = self.get_deltas(reference_entry, second_entry)
            return self.normalize(deltas)
        except KeyError:
            raise ValueError

    def normalize(self, deltas):
        return np.linalg.norm(deltas)

    def get_deltas(self, reference_entry, second_entry):
        reference_entry, second_entry = self.reorder_entries(reference_entry, second_entry)
        return self.calculate_deltas(reference_entry, second_entry)

    def calculate_deltas(self, first_entry, second_entry):
        deltas = []
        for (key, first_value), (_, second_value) in zip(first_entry.items(), second_entry.items()):
            deltas.append(self.weigh_delta((first_value - second_value), key))
        return deltas

    def weigh_delta(self, delta, key):
        return delta * (self.pre_normalize_weight(key))

    def pre_normalize_weight(self, key):
        # sqrt(weight * delta**2) --> sqrt(((weight ** 0.5) * delta)**2)
        return self.weight_or_default(key) ** 0.5

    def weight_or_default(self, key):
        return self.settings.weights().get(key, 1)

    def reorder_entries(self, reference_entry, second_entry):
        sorted_keys = sorted([key for key in reference_entry.keys() if key in self.settings.include()])
        reference_entry = {key: reference_entry[key] for key in sorted_keys}
        second_entry = {key: second_entry[key] for key in sorted_keys}
        return reference_entry, second_entry

    def get_closest_to(self, user_entry_dict):
        return self.get_closest_n(user_entry_dict, 1)[0]

    def get_closest_n(self, user_entry: dict, n: int):
        self.raise_if_invalid_number(n)
        self.raise_if_invalid_entry(user_entry)

        self.calculate_distances(user_entry)
        self.data: pd.DataFrame
        smallest_n = self.data.sort_values(by=DISTANCE)[:n]
        responses = [pd_util.get_dict_from_row(smallest_n.iloc[i: i+1]) for i in range(n)]
        self.remove_distance_column()
        return responses

    def remove_distance_column(self):
        self.data.drop(columns=DISTANCE, axis=1, inplace=True)

    def raise_if_invalid_number(self, n: int):
        if n > self.settings.max_n():
            raise ValueError(f"Cannot get more matches than {self.settings.max_n()}")

    def raise_if_invalid_entry(self, user_entry: dict):
        truth_list = [key in self.settings.include() for key in user_entry.keys()]
        if not any(truth_list):
            raise ValueError("Cannot recommend similar bike.")
