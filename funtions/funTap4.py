import pandas as pd
import numpy as np
import datetime as dt

from funtions import general

def name_file_head(name: str) -> str:
    now = dt.datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def valid_options(df: pd.DataFrame, dict_parameters: dict) -> list:

    return [dict_parameters[key]["columnLabel"] for key in dict_parameters if dict_parameters[key]["columnLabel"] in df.columns.tolist()]

def checkTimeData(df_data: pd.DataFrame, deltaMinutes: int):

    timeInfo = general.getTimeData(df_data)
    checkTime = False

    if len(timeInfo) > 0:
        check1 = timeInfo["deltaMinutes"] == deltaMinutes
        check2 = timeInfo["deltaDays"] % 1 == 0 and df_data.shape[0] % 24 == 0
        checkTime = all([check1, check2])

    return checkTime, timeInfo