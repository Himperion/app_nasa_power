import pandas as pd
import numpy as np
import streamlit as st
import random, io, yaml
from datetime import datetime, timedelta
import plotly.express as px

from funtions import general
from data.param import DICT_KEY_LABEL

dict_download = {
    "Xlsx": {
        "label": "Consumo eléctrico",
        "type_file": "xlsx",
        "fileName": "PES_addLoad",
        "nime": "xlsx",
        "emoji": "📄",
        "key": "PES_addLoad",
        "type": "primary"
    }
}

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

def checkTimeData(df_data: pd.DataFrame, deltaMinutes: int):

    timeInfo = getTimeData(df_data)
    checkTime = False

    if len(timeInfo) > 0:
        check1 = timeInfo["deltaMinutes"] == deltaMinutes
        check2 = timeInfo["deltaDays"] % 1 == 0 and df_data.shape[0] % 24 == 0
        checkTime = all([check1, check2])

    return checkTime, timeInfo

def addLoadData(df_data: pd.DataFrame, df_loadResized: pd.DataFrame, columnLoad: str, range_variation: tuple):

    min_variation, max_variation = int(range_variation[0][:-1])/100, int(range_variation[1][:-1])/100

    df_data[DICT_KEY_LABEL["LOAD"]] = 0.0

    for i in range(0,int(df_data.shape[0]/24),1):
        lowerValue, upperValue = 24*i, 24*(i+1)-1
        variation = np.random.uniform(min_variation, max_variation, size=len(df_loadResized)).tolist()
        list_values = df_loadResized[columnLoad].tolist()

        df_data.loc[lowerValue:upperValue, DICT_KEY_LABEL["LOAD"]] = [round(list_values[i]*(1+variation[i]), 3) for i in range(0,len(list_values),1)]

    return df_data

def name_file_head(name: str) -> str:
    now = datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def exampleCF(xi, xi_1, yi, yi_1, n, var, tol, iter):
    err, iter_count, alpha = 100, 0, 0.1
    err_values = []

    dx = (xi_1 - xi)/n
    xj = np.array([xi + (j-1)*dx for j in range(1, n+1, 1)])
    var_min, var_max = yi * (1 - var), yi * (1 + var)
    yj = np.array([random.uniform(var_min, var_max) for i in range(n)])

    while iter_count < iter and err > tol:
        dCF = 2*(np.mean(yj) - yi)
        pre_yj = yj - alpha*dCF
        err = (yi - np.mean(pre_yj))**2

        yj = pre_yj
        iter_count += 1
        err_values.append(err)

    err_values = np.array(err_values)
    mean_yj = np.mean(yj)

    return xj, yj, mean_yj, iter_count, err_values, var_min, var_max

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

def create_dataframe_nsamples(df_excel: pd.DataFrame, n_samples):
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

def to_excel(df: pd.DataFrame):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    
    processed_data = output.getvalue()
        
    return processed_data

def get_bytes_yaml(dictionary: dict):

    yaml_data = yaml.dump(dictionary, allow_unicode=True)

    buffer = io.BytesIO()
    buffer.write(yaml_data.encode('utf-8'))
    buffer.seek(0)

    return buffer

def get_list_tabs_graph(list_data_columns: list, list_options_columns_name: list, list_options_columns_label: list):

    list_tabs_graph_name, list_tabs_graph_label = [], []
    for i in range(0,len(list_data_columns),1):
        if list_data_columns[i] in list_options_columns_name:
            list_tabs_graph_name.append(list_data_columns[i])
            list_tabs_graph_label.append(list_options_columns_label[list_options_columns_name.index(list_data_columns[i])])

    return list_tabs_graph_name, list_tabs_graph_label