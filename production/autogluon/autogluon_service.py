import pandas as pd
from production.xml_handler import XmlHandler


class AutogluonService:
    def __init__(self):
        self.xml_handler = XmlHandler()

    def get_row(self, xml_request):
        self.xml_handler.set_xml(xml_request)
        model_input_dict = self.xml_handler.get_entries_dict()
        row = pd.DataFrame([list(model_input_dict.values())], columns=list(model_input_dict.keys()))
        print(row.to_dict())
        return row
