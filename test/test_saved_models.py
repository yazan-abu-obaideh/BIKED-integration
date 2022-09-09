import unittest
import keras
import sklearn.metrics
from keras.engine.sequential import Sequential
import tensorflow as tf
import pandas as pd
from src.load_data import load_framed_dataset
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from src.MultilabelPredictor import MultilabelPredictor

MODEL_DIR = "../resources/models/Trained Models/BestNN"
LABELS_DIR = "../resources/labels.txt"


class SavedLearningTest(unittest.TestCase):
    def setUp(self) -> None:
        self.k: Sequential
        self.labels = self.read_labels_from_file()
        self.k = keras.models.load_model(MODEL_DIR)
        self.p = tf.saved_model.load(MODEL_DIR)

    def test_can_get_model_summary(self):
        self.k.summary()

    def test_can_get_config(self):
        self.k.get_config()

    def test_can_get_first_layer_config(self):
        self.get_first_layer_config()

    def test_number_of_labels_is_number_of_inputs(self):
        assert len(self.labels) == self.get_first_layer_inputs()

    def test_can_load_data_and_train_model(self):
        data_train, y = self.original_loading_code()
        # TODO: ask Lyle to provide saved model!
        # self.original_training_code(data_train, y)

    def test_can_get_model_score(self):
        x_scaled, y, _, xscaler = load_framed_dataset("r", onehot=True, scaled=True, augmented=True)
        y_scaler = StandardScaler()
        y_scaler.fit(y)
        y_scaled = y_scaler.transform(y)
        x_scaled = x_scaled.values

        self.k: Sequential

        x_train, x_val, y_train, y_val = train_test_split(x_scaled, y_scaled, test_size=0.2, random_state=1)

        predictions = self.k.predict(x_train)
        print(predictions)
        print(y_val)

        print(sklearn.metrics.r2_score(predictions, y_train))

    def original_loading_code(self):
        x_scaled, y, _, x_scaler = self.standard_load()
        q = y.quantile(.95)
        for col in y.columns:
            y = y[y[col] <= q[col]]
        x_scaled = x_scaled.loc[y.index]
        y_scaler = StandardScaler()
        y_scaler.fit(y)
        y_scaled = y_scaler.transform(y)
        y_scaled = pd.DataFrame(y_scaled, columns=y.columns, index=y.index)
        xdata = x_scaled
        ydata = y_scaled
        data = pd.concat([xdata, ydata], axis=1)
        data_train, data_test, y_train, y_test = train_test_split(data, ydata, test_size=0.2, random_state=2021)
        x_train, x_test, y_train, y_test = train_test_split(xdata, ydata, test_size=0.2, random_state=2021)
        return data_train, y

    def original_training_code(self, data_train, y):
        predictor = MultilabelPredictor(y.columns)
        predictor.fit(train_data=data_train)

    def standard_load(self):
        return load_framed_dataset("r", onehot=True, scaled=True, augmented=True)

    def get_first_layer_inputs(self):
        NUM_INPUTS_INDEX = 1
        return self.get_first_layer_input_shape()[NUM_INPUTS_INDEX]

    def get_first_layer_input_shape(self):
        return self.get_first_layer_config()['batch_input_shape']

    def get_first_layer_config(self):
        return self.get_layer_config(layer_index=0)

    def get_layer_config(self, layer_index):
        return self.k.get_config()["layers"][layer_index]["config"]

    def read_labels_from_file(self):
        with open(LABELS_DIR, "r") as file:
            labels = [line.strip() for line in file.readlines()]
        return labels
