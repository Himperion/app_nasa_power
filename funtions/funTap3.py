import pandas as pd
import numpy as np
import random, io
from datetime import datetime, timedelta

def getTimeData(df_data: pd.DataFrame) -> dict:

    timeInfo = {}

    if "dates (Y-M-D hh:mm:ss)" in df_data.columns:
        time_0 = df_data.loc[0, "dates (Y-M-D hh:mm:ss)"].to_pydatetime()
        time_1 = df_data.loc[1, "dates (Y-M-D hh:mm:ss)"].to_pydatetime()

        timeInfo["deltaMinutes"] = (time_1 - time_0).total_seconds()/60
        timeInfo["dateIni"] = time_0
        timeInfo["dateEnd"] = df_data.loc[df_data.index[-1], "dates (Y-M-D hh:mm:ss)"].to_pydatetime()
        timeInfo["deltaDays"] = (timeInfo['dateEnd'] - timeInfo['dateIni']).days

    return timeInfo

def checkTimeData(df_data: pd.DataFrame, deltaMinutes: int, deltaDays: int):

    timeInfo = getTimeData(df_data)
    checkTime = False

    if len(timeInfo) > 0:
        check1 = timeInfo["deltaMinutes"] == deltaMinutes
        check2 = timeInfo["deltaDays"] >= deltaDays and timeInfo["deltaDays"] % 1 == 0
        checkTime = all([check1, check2])

    return checkTime, timeInfo

def addLoadData(df_data: pd.DataFrame, df_loadPU: pd.DataFrame, typeLoad: str, kWh_day: float, timeInfo: dict):

    factor = kWh_day/df_loadPU[typeLoad].sum()
    df_data['Load(kW)'] = 0.0

    for i in range(0,int(timeInfo["deltaDays"]),1):
        lowerValue, upperValue = 24*i, 24*(i+1)-1
        df_data.loc[lowerValue:upperValue, 'Load(kW)'] = [val*factor for val in df_loadPU[typeLoad].tolist()]
 
    return df_data

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