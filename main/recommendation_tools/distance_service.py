import pandas as pd


class DistanceService:
    def __init__(self, data):
        self.data = data

    def get_closest_to(self, user_entry_dict):
        self.data: pd.DataFrame
        self.data.apply(lambda x: [1, 2], axis=1)

    def distance_method(self, user_entry_dict, stored_entry):
        pass
