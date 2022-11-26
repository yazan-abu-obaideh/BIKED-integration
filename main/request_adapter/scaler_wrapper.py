import pandas as pd
import main.pandas_utility as pd_util


class ScalerWrapper:

    def __init__(self, scaler):
        self.scaler = scaler

    def scale(self, data: dict) -> dict:
        data = pd_util.get_row_from_dict(data)

        x_reg_sc = self.scaler.transform(data)
        x_reg = pd.DataFrame(x_reg_sc, columns=data.columns, index=data.index)

        return pd_util.get_dict_from_row(x_reg)

    def unscale(self, data: dict) -> dict:
        data = pd_util.get_row_from_dict(data)
        return self.unscale_dataframe(data)

    def unscale_dataframe(self, data: pd.DataFrame) -> dict:
        unscaled_values = self.scaler.inverse_transform(data)
        return pd_util.get_dict_from_row(pd.DataFrame(unscaled_values,
                                                      columns=data.columns,
                                                      index=data.index))
