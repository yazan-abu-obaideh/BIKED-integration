from abc import abstractmethod, ABCMeta

import numpy as np
import pandas as pd

from service.main.processing.processing_pipeline import ProcessingPipeline
from service.main.recommendation.similarity_engine_settings import EngineSettings

DISTANCE = 'distance_from_user_entry'


class SimilarityEngine(metaclass=ABCMeta):
    @abstractmethod
    def get_closest_to(self, user_entry_dict):
        pass

    @abstractmethod
    def get_closest_index_to(self, user_entry_dict):
        pass

    @abstractmethod
    def get_closest_n(self, user_entry: dict, n: int):
        pass

    @abstractmethod
    def get_closest_n_indexes(self, user_entry: dict, n: int):
        pass

    @abstractmethod
    def get_settings(self) -> EngineSettings:
        pass


class SimilarityRequest:
    def __init__(self, n: int, request: dict):
        self.n = n
        self.request = request


class EuclideanSimilarityEngine(SimilarityEngine):
    def __init__(self, data, settings: EngineSettings):
        self.data = data
        self.settings = settings
        self.raise_if_invalid_configuration()
        _processing_pipeline = ProcessingPipeline(steps=[
            self._validate,
            self._calculate_distances,
            self._get_closest_n
        ])
        self._get_closest_pipeline = ProcessingPipeline(steps=[
            _processing_pipeline.process,
            self._build_response
        ])
        self._get_closest_indexes_pipeline = ProcessingPipeline(steps=[
            _processing_pipeline.process,
            self._build_index_response
        ])

    def raise_if_invalid_configuration(self):
        desired = self.get_settings().include()
        actual = self.data.columns.values
        if not set(desired).issubset(set(actual)):
            raise ValueError("Similarity engine configured incorrectly. "
                             "Columns included in the settings do not match dataset columns.")

    def get_settings(self) -> EngineSettings:
        return self.settings

    def get_closest_to(self, user_entry_dict):
        return self.get_closest_n(user_entry_dict, 1)[0]

    def get_closest_index_to(self, user_entry_dict):
        return self.get_closest_n_indexes(user_entry_dict, 1)[0]

    def get_closest_n(self, user_entry: dict, n: int):
        return self._get_closest(user_entry,
                                 n,
                                 lambda closest_n_rows: [self._build_response(row) for row in closest_n_rows.items()])

    def get_closest_n_indexes(self, user_entry: dict, n: int):
        return self._get_closest(user_entry,
                                 n,
                                 lambda closest_n_rows: [self._build_index_response(row) for row in
                                                         closest_n_rows.items()])

    def _build_response(self, row):
        response = self.data.loc[row[0]].to_dict()
        response.update({"distance_from_user_entry": row[1]})
        return response

    def _build_index_response(self, row):
        return row[0]

    def _get_closest(self, user_entry: dict, n: int, response_builder: callable):
        self._validate(n, user_entry)
        distances = self._calculate_distances(user_entry)
        closest_n = self._get_closest_n(distances, n)
        responses = response_builder(closest_n)
        return responses

    def _get_closest_n(self, distances, n):
        closest_n = distances.sort_values()[:n]
        return closest_n

    def _validate(self, n, user_entry):
        self._raise_if_invalid_number(n)
        self._raise_if_invalid_entry(user_entry)

    def _calculate_distances(self, user_entry_dict: dict) -> pd.Series:
        self.data: pd.DataFrame
        filtered_user_entry = self._get_wanted_entries(user_entry_dict)

        def distance_from_user_entry(row):
            return self._get_distance_between(filtered_user_entry, row)

        return self.data.apply(distance_from_user_entry, axis=1)

    def _get_wanted_entries(self, user_entry_dict):
        return {key: value for key, value in user_entry_dict.items() if key in self.settings.include()}

    def _get_distance_between(self, reference_entry, second_entry):
        try:
            deltas = self._get_deltas(reference_entry, second_entry)
            return self._normalize(deltas)
        except KeyError:
            raise ValueError

    def _normalize(self, deltas):
        return np.linalg.norm(deltas)

    def _get_deltas(self, reference_entry, second_entry):
        reference_entry, second_entry = self._reorder_entries(reference_entry, second_entry)
        return self._calculate_deltas(reference_entry, second_entry)

    def _calculate_deltas(self, first_entry, second_entry):
        deltas = []
        for (key, first_value), (_, second_value) in zip(first_entry.items(), second_entry.items()):
            deltas.append(self._weigh_delta((first_value - second_value), key))
        return deltas

    def _weigh_delta(self, delta, key):
        return delta * (self._pre_normalize_weight(key))

    def _pre_normalize_weight(self, key):
        # sqrt(weight * delta**2) --> sqrt(((weight ** 0.5) * delta)**2)
        return self._weight_or_default(key) ** 0.5

    def _weight_or_default(self, key):
        return self.settings.weights().get(key, 1)

    def _reorder_entries(self, reference_entry, second_entry):
        sorted_keys = sorted([key for key in reference_entry.keys() if key in self.settings.include()])
        reference_entry = {key: reference_entry[key] for key in sorted_keys}
        second_entry = {key: second_entry[key] for key in sorted_keys}
        return reference_entry, second_entry

    def _raise_if_invalid_number(self, n: int):
        if n > self.settings.max_n():
            raise ValueError(f"Cannot get more matches than {self.settings.max_n()}")

    def _raise_if_invalid_entry(self, user_entry: dict):
        truth_list = [key in self.settings.include() for key in user_entry.keys()]
        if not any(truth_list):
            raise ValueError("Cannot provide similar entry.")
