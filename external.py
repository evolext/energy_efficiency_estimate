import pandas as pd
import numpy as np


def get_variable_names(filepath):
    table = pd.read_csv(filepath)
    return list(table.columns)


def calculate_point_estimate(filepath_base, filepath_report, feature_name):
    ts_base = pd.read_csv(filepath_base)[feature_name].to_numpy()
    ts_report = pd.read_csv(filepath_report)[feature_name].to_numpy()
    return np.sum(ts_base - ts_report)


def calculate_interval_estimate(filepath_interval_forecast, filepath_actual, feature_name_upper, feature_name_lower, feature_name_actual):
    ts_upper = pd.read_csv(filepath_interval_forecast)[feature_name_upper].to_numpy()
    ts_lower = pd.read_csv(filepath_interval_forecast)[feature_name_lower].to_numpy()

    ts_actual = pd.read_csv(filepath_actual)[feature_name_actual].to_numpy()

    return np.sum(ts_upper - ts_actual), np.sum(ts_lower - ts_actual)





