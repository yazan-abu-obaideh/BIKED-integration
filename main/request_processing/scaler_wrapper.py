from sklearn.preprocessing import StandardScaler
import main.pandas_utility as pd_util
import pandas as pd


class ScalerWrapper:

    def __init__(self, scaler, columns_in_order):
        self.scaler = scaler
        self.columns_in_order = columns_in_order

    def scale(self, data: dict) -> dict:
        return self.operate_on(data, self._scale_dataframe)

    def unscale(self, data: dict) -> dict:
        return self.operate_on(data, self._unscale_dataframe)

    def operate_on(self, data: dict, function_on_data: callable):
        data = self.reorder(data)
        return pd_util.get_dict_from_row(function_on_data(data))

    def _scale_dataframe(self, unscaled_data: pd.DataFrame):
        scaled_values = self.scaler.transform(unscaled_data)
        scaled_dataframe = self._rebuild_dataframe(scaled_values, unscaled_data)
        return scaled_dataframe

    def _rebuild_dataframe(self, values, original_dataframe):
        return pd.DataFrame(values,
                            columns=original_dataframe.columns,
                            index=original_dataframe.index)

    def _unscale_dataframe(self, scaled_data: pd.DataFrame) -> pd.DataFrame:
        unscaled_values = self.scaler.inverse_transform(scaled_data)
        return self._rebuild_dataframe(unscaled_values, scaled_data)
    @classmethod
    def build_from_dataframe(cls, data):
        scaler = StandardScaler()
        scaler.fit(data)
        return ScalerWrapper(scaler, data.columns)


    def reorder(self, data):
        data = pd_util.get_row_from_dict(data)[self.columns_in_order]
        return data
