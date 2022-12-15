from sklearn.preprocessing import StandardScaler
import main.pandas_utility as pd_util
import pandas as pd


class ScalerWrapper:

    def __init__(self, scaler, columns_in_order):
        self.scaler = scaler
        self.columns_in_order = columns_in_order

    def scale(self, data: dict) -> dict:
        return self._operate_on(data, self.scale_dataframe)

    def unscale(self, data: dict) -> dict:
        return self._operate_on(data, self.unscale_dataframe)

    def scale_dataframe(self, unscaled_data: pd.DataFrame):
        return self._operate_on_dataframe(unscaled_data, self.scaler.transform)

    def unscale_dataframe(self, scaled_data: pd.DataFrame) -> pd.DataFrame:
        return self._operate_on_dataframe(scaled_data, self.scaler.inverse_transform)

    def _operate_on(self, data: dict, operate: callable):
        data = self.reorder(data)
        return pd_util.get_dict_from_row(operate(data))

    def _operate_on_dataframe(self, dataframe: pd.DataFrame, operation: callable):
        new_values = operation(dataframe)
        return self._rebuild_dataframe(new_values, dataframe)

    def _rebuild_dataframe(self, values, original_dataframe):
        return pd.DataFrame(values,
                            columns=original_dataframe.columns,
                            index=original_dataframe.index)
    @classmethod
    def build_from_dataframe(cls, data):
        scaler = StandardScaler()
        scaler.fit(data)
        return ScalerWrapper(scaler, data.columns)


    def reorder(self, data):
        data = pd_util.get_row_from_dict(data)[self.columns_in_order]
        return data
