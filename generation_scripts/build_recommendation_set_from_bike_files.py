from service.main.processing.bike_xml_handler import BikeXmlHandler
from service.main.recommendation.default_engine_settings import DefaultBikeSettings
import service.main.processing.pandas_utility as pd_util
import pandas as pd
import os

FILENAME_KEY = "filename"

include = DefaultBikeSettings().include()
dataframe = pd.DataFrame(columns=include + [FILENAME_KEY]).set_index(FILENAME_KEY)
xml_handler = BikeXmlHandler()

bike_files_dir_path = "bikecad_files_gen"
for filename in os.listdir(bike_files_dir_path):
    with open(f"{bike_files_dir_path}/{filename}", "r") as file:
        xml_handler.set_xml(file.read())
        entries_dict = xml_handler.get_entries_dict()
        entries_dict = {key: value for key, value in entries_dict.items() if key in include}
        entries_dict[FILENAME_KEY] = filename
        dataframe = pd.concat([pd_util.get_single_row_dataframe_from(entries_dict), dataframe])

generated_dataframe = dataframe.set_index(FILENAME_KEY)
generated_dataframe.to_csv(path_or_buf="BIKED_recommend.csv")
