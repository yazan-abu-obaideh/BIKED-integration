import pandas as pd
import main.pandas_utility as pd_util


def OH_encode(data):
    data = data.copy()
    # One-hot encode the materials
    data.loc[:, "Material"] = pd.Categorical(data["Material"], categories=["Steel", "Aluminum", "Titanium"])
    mats_oh = pd.get_dummies(data["Material"], prefix="Material=", prefix_sep="")
    data.drop(["Material"], axis=1, inplace=True)
    data = pd.concat([mats_oh, data], axis=1)
    return data


class RequestScaler:

    def __init__(self, scaler):
        self.scaler = scaler

    def scale(self, row):

        row = pd_util.get_row_from_dict(row)

        x_reg = row.iloc[:, :-11]

        x_reg = OH_encode(x_reg)

        x_reg_sc = self.scaler.transform(x_reg)
        x_reg = pd.DataFrame(x_reg_sc, columns=x_reg.columns, index=x_reg.index)

        return x_reg.iloc[0].to_dict()
