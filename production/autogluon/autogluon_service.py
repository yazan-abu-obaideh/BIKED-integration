import pandas as pd
from production.xml_handler import XmlHandler
from production.autogluon.autogluon_wrapper import AutogluonPredictorWrapper
from production.request_adapter import RequestAdapter


class AutogluonService:
    def __init__(self):
        self.xml_handler = XmlHandler()
        self.predictor = AutogluonPredictorWrapper()
        self.adapter = RequestAdapter()

    def get_row(self, adapted_request_dict):
        model_input_dict = {key: float(value) for key, value in adapted_request_dict.items()}
        one_row_df = pd.DataFrame([list(model_input_dict.values())], columns=list(model_input_dict.keys()))
        return one_row_df

    def get_dict_from_row(self, row):
        return row.loc[self.first_row_index(row)].to_dict()

    def first_row_index(self, dataframe):
        return dataframe.index.values[0]

    def predict(self, bike_cad_xml) -> dict:
        bike_cad_dict = self.adapter.convert(bike_cad_xml)
        row = self.get_row(bike_cad_dict)
        return self.get_dict_from_row(self.predictor.predict(row))
