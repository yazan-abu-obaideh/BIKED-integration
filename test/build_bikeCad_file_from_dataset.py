from main.load_data import load_framed_dataset
import pandas as pd
import os

prefix = os.path.join(os.path.dirname(__file__), "../resources")


x_scaled, y, _, xscaler = (load_framed_dataset("r", onehot=True, scaled=True, augmented=True))
data = pd.read_csv(os.path.abspath(prefix + "/all_structural_data_aug.csv"), index_col=0)
print(data.head())
