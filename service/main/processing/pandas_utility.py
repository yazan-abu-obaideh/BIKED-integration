import pandas as pd


def get_single_row_dataframe_from(dictionary: dict) -> pd.DataFrame:
    return pd.DataFrame([list(dictionary.values())], columns=list(dictionary.keys()))


def get_dict_from_first_row(dataframe: pd.DataFrame) -> dict:
    return dataframe.loc[__first_row_index(dataframe)].to_dict()


def __first_row_index(dataframe) -> int:
    return dataframe.index.values[0]
