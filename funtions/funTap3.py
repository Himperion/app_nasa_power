import pandas as pd
import numpy as np
import random, io
from datetime import datetime, timedelta

def name_file_head(name: str) -> str:
    now = datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

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

def aplicar_gradient(row, n_samples, alpha, tol, iter_max, variation, data_columns):
    new_rows = []
    values_predict = {datos: gradient_descent_LR(row[datos], n_samples, variation, alpha, tol, iter_max) for datos in data_columns}
    for i in range(n_samples):
        new_row = [round(values_predict[datos][i], 4) for datos in data_columns]
        new_rows.append(new_row)

    return new_rows

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

def process_data(out: pd.DataFrame, n_samples: int, dict_params:dict, constants_GD: dict) -> pd.DataFrame:

    alpha, tol, iter_max = constants_GD["alpha"], constants_GD["tol"], constants_GD["iter_max"]
    df_excel, dataColumns, variation = dict_params['df_excel'], dict_params['dataColumns'], dict_params['variation']

    aux = np.vstack(df_excel.apply(lambda row: aplicar_gradient(row, n_samples, alpha, tol, iter_max, variation, dataColumns), axis=1).explode().to_numpy())
    aux_df = pd.DataFrame(aux, columns=dataColumns)
    common_columns = aux_df.columns.intersection(out.columns)
    out[common_columns] = aux_df[common_columns]

    return out

def get_excel_bytes(out: pd.DataFrame):

    excel_bytes_io = io.BytesIO()
    out.to_excel(excel_bytes_io, index=False)
    excel_bytes_io.seek(0)

    return excel_bytes_io