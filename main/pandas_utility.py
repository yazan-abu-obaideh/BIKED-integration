import pandas as pd


def get_row(adapted_request_dict):
    model_input_dict = {key: float(value) for key, value in adapted_request_dict.items()}
    return get_row_from_dict(model_input_dict)


def get_row_from_dict(model_input_dict):
    return pd.DataFrame([list(model_input_dict.values())], columns=list(model_input_dict.keys()))


def get_dict_from_row(row):
    return row.loc[first_row_index(row)].to_dict()


def first_row_index(dataframe):
    return dataframe.index.values[0]
