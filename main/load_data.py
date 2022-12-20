# -*- coding: utf-8 -*-
"""
Created on Sun Jul 10 12:05:43 2022

@author: Lyle
"""
import os.path

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

FILE_PATH = os.path.dirname(__file__)


def one_hot_encode_material(data):
    data = data.copy()
    # One-hot encode the materials
    data.loc[:, "Material"] = pd.Categorical(data["Material"], categories=["Steel", "Aluminum", "Titanium"])
    mats_oh = pd.get_dummies(data["Material"], prefix="Material=", prefix_sep="")
    data.drop(["Material"], axis=1, inplace=True)
    data = pd.concat([mats_oh, data], axis=1)
    return data


def load_augmented_framed_dataset():
    reg_data = pd.read_csv(os.path.join(FILE_PATH, "../resources/datasets/all_structural_data_aug.csv"), index_col=0)

    x = reg_data.iloc[:, :-11]

    x = one_hot_encode_material(x)

    x, x_scaler = scale(x)
    y = reg_data.iloc[:, -11:-1]

    for col in ['Sim 1 Safety Factor', 'Sim 3 Safety Factor']:
        y[col] = 1 / y[col]
        y.rename(columns={col: col + " (Inverted)"}, inplace=True)
    for col in ['Sim 1 Dropout X Disp.', 'Sim 1 Dropout Y Disp.', 'Sim 1 Bottom Bracket X Disp.',
                'Sim 1 Bottom Bracket Y Disp.', 'Sim 2 Bottom Bracket Z Disp.', 'Sim 3 Bottom Bracket Y Disp.',
                'Sim 3 Bottom Bracket X Rot.', 'Model Mass']:
        y[col] = [np.abs(val) for val in y[col].values]
        y.rename(columns={col: col + " Magnitude"}, inplace=True)
    y = filter_y(y)
    x = x.loc[y.index]
    y, y_scaler = scale(y)

    return x, y, x_scaler, y_scaler


def scale(v):
    v_scaler = StandardScaler()
    v_scaler.fit(v)
    v_scaled_values = v_scaler.transform(v)
    new_v = pd.DataFrame(v_scaled_values, columns=v.columns, index=v.index)
    return new_v, v_scaler


def filter_y(y):
    q = y.quantile(.95)
    for col in y.columns:
        y = y[y[col] <= q[col]]
    return y
