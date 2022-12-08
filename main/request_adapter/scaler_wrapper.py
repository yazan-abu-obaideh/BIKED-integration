import pandas as pd
import main.pandas_utility as pd_util


class ScalerWrapper:

    def __init__(self, scaler, columns_in_order):
        self.scaler = scaler
        self.columns_in_order = columns_in_order

    def scale(self, data: dict) -> dict:
        data = self.reorder(data)

        x_reg_sc = self.scaler.transform(data)
        x_reg = pd.DataFrame(x_reg_sc, columns=data.columns, index=data.index)

        return pd_util.get_dict_from_row(x_reg)

    def unscale(self, data: dict) -> dict:
        data = self.reorder(data)
        return self._unscale_dataframe(data)

    def _unscale_dataframe(self, data: pd.DataFrame) -> dict:
        unscaled_values = self.scaler.inverse_transform(data)
        return pd_util.get_dict_from_row(pd.DataFrame(unscaled_values,
                                                      columns=data.columns,
                                                      index=data.index))

    def reorder(self, data):
        data = pd_util.get_row_from_dict(data)[self.columns_in_order]
        return data
