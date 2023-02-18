from abc import ABCMeta, abstractmethod
import pandas as pd


class Predictor(metaclass=ABCMeta):
    @abstractmethod
    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        pass