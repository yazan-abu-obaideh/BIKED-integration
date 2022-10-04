import pandas as pd
from production.xml_handler import XmlHandler
from production.autogluon.autogluon_wrapper import AutogluonPredictorWrapper


class AutogluonService:
    def __init__(self):
        self.xml_handler = XmlHandler()
        self.predictor = AutogluonPredictorWrapper()

    def get_row(self, xml_request):
        self.xml_handler.set_xml(xml_request)
        model_input_dict = {key: float(value) for key, value in self.xml_handler.get_entries_dict().items()}
        one_row_df = pd.DataFrame([list(model_input_dict.values())], columns=list(model_input_dict.keys()))
        return one_row_df

    def get_dict_from_row(self, row):
        return row.loc[self.first_row_index(row)].to_dict()

    def first_row_index(self, dataframe):
        return dataframe.index.values[0]

    def predict(self, bike_cad_xml) -> dict:
        row = self.get_row(bike_cad_xml)
        return self.get_dict_from_row(self.predictor.predict(row))
