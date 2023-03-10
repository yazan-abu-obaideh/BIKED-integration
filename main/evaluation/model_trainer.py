from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

from main.load_data import load_augmented_framed_dataset
from main.evaluation.MultilabelPredictor import MultilabelPredictor

import pandas as pd

x_scaled, y_scaled, x_scaler, y_scaler = load_augmented_framed_dataset()

x_train, x_test, y_train, y_test = train_test_split(x_scaled, y_scaled)

x_scaled = x_scaled[:100]
y_scaled = y_scaled[:100]
my_predictor = MultilabelPredictor(labels=y_scaled.columns)
my_predictor.fit(
    train_data=pd.concat([x_train, y_train], axis=1)
)
predictions = my_predictor.predict(x_test)
r2 = r2_score(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
mae = mean_absolute_error(y_test, predictions)
print(f"{r2=}")
print(f"{mse=}")
print(f"{mae=}")
