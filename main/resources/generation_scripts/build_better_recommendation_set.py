from main.xml_handler import XmlHandler
from main.recommendation.bike_recommendation_service import DefaultBikeSettings
import main.pandas_utility as pd_util
import pandas as pd

FILENAME_KEY = "filename"

include = DefaultBikeSettings().include()
dataframe = pd.DataFrame(columns=include + [FILENAME_KEY]).set_index(FILENAME_KEY)
xml_handler = XmlHandler()
for i in range(1, 10):
    filename = f"({i}).bcad"
    with open(f"../large/bikecad files/{filename}", "r") as file:
        xml_handler.set_xml(file.read())
        entries_dict = xml_handler.get_entries_dict()
        entries_dict = {key: value for key, value in entries_dict.items() if key in include}
        entries_dict[FILENAME_KEY] = filename
        dataframe = pd.concat([pd_util.get_row_from_dict(entries_dict), dataframe])

print(dataframe.set_index(FILENAME_KEY))
