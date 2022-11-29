import pandas as pd
import numpy as np
import main.pandas_utility as pd_util
from main.recommendation.recommendation_service_settings import RecommendationSettings

DISTANCE = 'distance_from_user_entry'


class RecommendationService:
    def __init__(self, data, settings: RecommendationSettings):
        self.data = data
        # TODO: USE the sheet provided
        self.settings = settings

        # TODO: make it so the distance service remains completely agnostic of the type of data,
        #  the settings, the scaling and unscaling required - because this service CAN be concrete.
        #  Do this right and you won't have to change anything about this package if the dataset changes.

    def get_distance_between(self, first_entry, second_entry):
        return np.linalg.norm(pd.Series(first_entry).values - pd.Series(second_entry).values)

    def get_closest_to(self, user_entry_dict):
        return self.get_closest_n(user_entry_dict, 1)[0]

    def get_closest_n(self, user_entry, n):
        self.raise_if_invalid_number(n)

        self.calculate_distances(user_entry)
        smallest_n = self.data.sort_values(by=DISTANCE)[DISTANCE].values[:n]
        responses = [self.get_response_by_distance(distance) for distance in smallest_n]
        self.remove_distance_column()
        return responses

    def remove_distance_column(self):
        self.data.drop(columns=DISTANCE, axis=1, inplace=True)

    def calculate_distances(self, user_entry_dict):
        self.data: pd.DataFrame
        user_entry_row = pd.Series(user_entry_dict)

        def distance_from_user_entry(row):
            return self.get_distance_between(row, user_entry_row)

        self.data[DISTANCE] = self.data.apply(distance_from_user_entry, axis=1)

    def get_response_by_distance(self, smallest_distance) -> dict:
        correct_row_index = self.data[self.data[DISTANCE] == smallest_distance].index[0]
        return pd_util.get_dict_from_row(self.data[self.data.index == correct_row_index])

    def raise_if_invalid_number(self, n):
        if n > self.settings.max_n():
            raise ValueError(f"Cannot get more matches than {self.settings.max_n()}")
