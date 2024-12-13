import pandas as pd
import numpy as np
import datetime as dt


def name_file_head(name: str) -> str:
    now = dt.datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def valid_options(df: pd.DataFrame, dict_parameters: dict) -> list:

    return [dict_parameters[key]["columnLabel"] for key in dict_parameters if dict_parameters[key]["columnLabel"] in df.columns.tolist()]

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