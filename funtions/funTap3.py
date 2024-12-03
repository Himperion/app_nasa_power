import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta



def valid_options(df: pd.DataFrame, dict_parameters: dict) -> list:

    return [v[1] for k, v in dict_parameters.items() if v[1] in df.columns.tolist()]

def gradient_descent_LR(value, n, variation, alpha, tol, iter_max):
    err, iter_count = 100, 0
    if np.any(value == 0.0):
        return np.zeros(n)
    else:
        range_min, range_max = value * (1 - variation), value * (1 + variation)
        xi = np.array([random.uniform(range_min, range_max) for i in range(n)])
        while iter_count < iter_max and err > tol:
            dL_xi = (2 / n) * (np.mean(xi) - value)
            xi_predict = xi - alpha * dL_xi
            err = abs(np.mean(xi_predict) - value)
            xi = xi_predict
            iter_count += 1
        return xi_predict

def create_dataframe_nsamples(df_excel, n_samples):
    out = pd.DataFrame()
    for col in df_excel.columns:
        out[col] = df_excel[col].repeat(n_samples).reset_index(drop=True)
    return out

def modify_time_interval(out:pd.DataFrame, delta_time_m:int):
    if "dates (Y-M-D hh:mm:ss)" in list(out.columns):
        out["dates (Y-M-D hh:mm:ss)"] = pd.to_datetime(out["dates (Y-M-D hh:mm:ss)"] )
        increment = timedelta(minutes=delta_time_m)
        for index, row in out.iterrows():
            if index == 0:
                last_time = row["dates (Y-M-D hh:mm:ss)"]
            else: 
                last_time += increment
                out.at[index,"dates (Y-M-D hh:mm:ss)"]=last_time
    return out

def aplicar_gradient(row, n_samples, alpha, tol, iter_max, variation, data_columns):
    new_rows = []
    values_predict = {datos: gradient_descent_LR(row[datos], n_samples, variation, alpha, tol, iter_max) for datos in data_columns}
    for i in range(n_samples):
        new_row = [round(values_predict[datos][i], 4) for datos in data_columns]
        new_rows.append(new_row)

    return new_rows

def process_data(df_excel, data_columns, out, n_samples, variation, alpha, tol, iter_max):
    aux = np.vstack(df_excel.apply(lambda row: aplicar_gradient(row, n_samples, alpha, tol, iter_max, variation, data_columns), axis=1).explode().to_numpy())
    aux_df = pd.DataFrame(aux, columns=data_columns)
    common_columns = aux_df.columns.intersection(out.columns)
    out[common_columns] = aux_df[common_columns]

    return out
