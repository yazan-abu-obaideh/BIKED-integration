import pandas as pd
import numpy as np
import pandas_utility as pd_util

DISTANCE = 'distance_from_user_entry'


class DistanceService:
    def __init__(self, data):
        self.data = data

    def get_distance_between(self, first_entry, second_entry):
        return np.linalg.norm(pd.Series(first_entry).values - pd.Series(second_entry).values)

    def get_closest_to(self, user_entry_dict):

        self.data: pd.DataFrame
        user_entry_row = pd.Series(user_entry_dict)

        def distance_from_user_entry(row):
            return self.get_distance_between(row, user_entry_row)

        self.data[DISTANCE] = self.data.apply(distance_from_user_entry, axis=1)
        smallest_distance = min(self.data[DISTANCE].values)

        correct_row_index = self.data[self.data[DISTANCE] == smallest_distance].index[0]
        response = pd_util.get_dict_from_row(self.data[self.data.index == correct_row_index])

        self.data.drop(columns=DISTANCE, axis=1, inplace=True)

        return response
