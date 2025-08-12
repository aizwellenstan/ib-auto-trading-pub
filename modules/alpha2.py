import numpy as np
import pandas as pd
from scipy.stats import zscore

def ts_decay_linear(data, n):
    weights = np.arange(1, n + 1)
    decayed_data = data
    for i in range(n, len(data)):
        decayed_data[i] = np.dot(data[i-n+1:i+1][::-1], weights) / weights.sum()
    return decayed_data

def group_zscore(data):
    std = np.std(data)
    if std == 0:
        return np.zeros_like(data)
    else:
        return (data - np.mean(data)) / std

def winsorize(data, std):
    data_mean = data.mean()
    data_std = data.std()
    lower_bound = data_mean - std * data_std
    upper_bound = data_mean + std * data_std
    data[data < lower_bound] = lower_bound
    data[data > upper_bound] = upper_bound
    return data

def days_from_last_change(data, n):
    return (data != np.roll(data, 1)).cumsum()

def log(data):
    return np.log(data)

def log1(data):
    return np.log1p(data)

def vector_neut(data1, data2):
    return data1 - data2

def Alpha2(npArr):
    data = npArr
    data_gpz = winsorize(ts_decay_linear(data, 252), std=4.0)
    data_adj = data_gpz * (1 + log1(days_from_last_change(data, 63)) + 1)
    result = winsorize(group_zscore(vector_neut(data_adj, np.mean(data_adj))), std=4.0)
    return result
