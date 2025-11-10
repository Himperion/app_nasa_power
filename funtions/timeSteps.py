import pandas as pd
import streamlit as st

from funtions import general
from data.param import DICT_PARAMS, DICT_PARAMS_LABEL_KEY

def getVarAux(df_columns: list):

    dictItems = {
        "ALLSKY_SFC_SW_DWN": "HSP ({0})",
        "LOAD": "Load (kWh/{0})"
    }

    listKeys = list(dictItems.keys())
    listLabels = [DICT_PARAMS[key]["Label"] for key in listKeys]

    listColumns = []
    for column in listLabels:
        if column in df_columns:
            listColumns.append(column)

    dictReplace = {"dates (Y-M-D hh:mm:ss)": "Fecha"}
    for label in listColumns:
        if DICT_PARAMS_LABEL_KEY[label] in dictItems:
            dictReplace = {**dictReplace, **{label: dictItems[DICT_PARAMS_LABEL_KEY[label]]}}

    return dictReplace, listColumns

def getDfGrouper(df: pd.DataFrame, listColumns: list, freq: str) -> pd.DataFrame:

    dfGrouper = df.groupby(pd.Grouper(key='dates (Y-M-D hh:mm:ss)', freq=freq))[listColumns].sum().reset_index()

    return dfGrouper

def getDfGrouperDay(df: pd.DataFrame, listColumns: list, deltaMinutes: float) -> pd.DataFrame:

    deltaHours = deltaMinutes/60
    
    df_day = getDfGrouper(df=df, listColumns=listColumns, freq="D")

    if DICT_PARAMS["ALLSKY_SFC_SW_DWN"]["Label"] in df.columns.to_list():
        df_day[DICT_PARAMS["ALLSKY_SFC_SW_DWN"]["Label"]] = round((df_day[DICT_PARAMS["ALLSKY_SFC_SW_DWN"]["Label"]]*deltaHours)/1000, 3)
    if DICT_PARAMS["LOAD"]["Label"] in df_day.columns.to_list():
        df_day[DICT_PARAMS["LOAD"]["Label"]] = round((df_day[DICT_PARAMS["LOAD"]["Label"]]*deltaHours), 3)

    return df_day

def getDfsTimeLapse(df: pd.DataFrame, timeInfo: dict):

    df_day, df_month, df_year = None, None, None

    dictReplace, listColumns = getVarAux(df_columns=df.columns.to_list())

    if timeInfo["deltaDays"] > 0:
        df_day = getDfGrouperDay(df=df, listColumns=listColumns, deltaMinutes=timeInfo["deltaMinutes"])
    if timeInfo["deltaMonths"] > 0:
        df_month = getDfGrouper(df=df_day, listColumns=listColumns, freq="M")
    if timeInfo["deltaYears"] > 0:
        df_year = getDfGrouper(df=df_month, listColumns=listColumns, freq="Y")

    if df_day is not None:
        df_day["dates (Y-M-D hh:mm:ss)"] = df_day["dates (Y-M-D hh:mm:ss)"].dt.date
        dictReplaceLabel = {k: v.format("día") for k, v in dictReplace.items()}
        df_day.rename(columns=dictReplaceLabel, inplace=True)
    if df_month is not None:
        df_month["dates (Y-M-D hh:mm:ss)"] = df_month["dates (Y-M-D hh:mm:ss)"].dt.date
        dictReplaceLabel = {k: v.format("mes") for k, v in dictReplace.items()}
        df_month.rename(columns=dictReplaceLabel, inplace=True)
    if df_month is not None:
        df_year["dates (Y-M-D hh:mm:ss)"] = df_year["dates (Y-M-D hh:mm:ss)"].dt.date
        dictReplaceLabel = {k: v.format("año") for k, v in dictReplace.items()}
        df_year.rename(columns=dictReplaceLabel, inplace=True)

    return df_day, df_month, df_year

def viewDfsTimeLapse(key: str, df_day: pd.DataFrame|None, df_month: pd.DataFrame|None, df_year: pd.DataFrame|None, timeInfo: dict):

    dictParamsDfTime = {}

    if key == "ALLSKY_SFC_SW_DWN":
        if df_day is not None:
            dictAux = {
                "df": df_day, "x": "Fecha", "y": "HSP (día)", "color": DICT_PARAMS["ALLSKY_SFC_SW_DWN"]["Color"],
                "value_label": "HSP", "title": "Hora Solar Pico (día)",
                "timeInfo": timeInfo, "rangeSelector": True, "rangeSlider": True
            }
            dictParamsDfTime["HSP (día)"] = dictAux
        if df_month is not None:
            dictAux = {
                "df": df_month, "x": "Fecha", "y": "HSP (mes)", "color": DICT_PARAMS["ALLSKY_SFC_SW_DWN"]["Color"],
                "value_label": "HSP", "title": "Hora Solar Pico (mes)",
                "timeInfo": None, "rangeSelector": False, "rangeSlider": True
            }
            dictParamsDfTime["HSP (mes)"] = dictAux
        if df_month is not None:
            dictAux = {
                "df": df_year, "x": "Fecha", "y": "HSP (año)", "color": DICT_PARAMS["ALLSKY_SFC_SW_DWN"]["Color"],
                "value_label": "HSP", "title": "Hora Solar Pico (mes)",
                "timeInfo": None, "rangeSelector": False, "rangeSlider": False
            }
            dictParamsDfTime["HSP (año)"] = dictAux

    elif key == "LOAD":
        if df_day is not None:
            dictAux = {
                "df": df_day, "x": "Fecha", "y": "Load (kWh/día)", "color": DICT_PARAMS["LOAD"]["Color"],
                "value_label": "Demanda (kWh/día)", "title": "Demanda eléctrica (día)",
                "timeInfo": timeInfo, "rangeSelector": True, "rangeSlider": True
            }
            dictParamsDfTime["Demanda eléctrica (día)"] = dictAux
        if df_month is not None:
            dictAux = {
                "df": df_month, "x": "Fecha", "y": "Load (kWh/mes)", "color": DICT_PARAMS["LOAD"]["Color"],
                "value_label": "Demanda (kWh/mes)", "title": "Demanda eléctrica (mes)",
                "timeInfo": None, "rangeSelector": False, "rangeSlider": True
            }
            dictParamsDfTime["Demanda eléctrica (mes)"] = dictAux
        if df_month is not None:
            dictAux = {
                "df": df_year, "x": "Fecha", "y": "Load (kWh/año)", "color": DICT_PARAMS["LOAD"]["Color"],
                "value_label": "Demanda (kWh/año)", "title": "Demanda eléctrica (año)",
                "timeInfo": None, "rangeSelector": False, "rangeSlider": False
            }
            dictParamsDfTime["Demanda eléctrica (año)"] = dictAux


    listKeysDicts = [key for key in dictParamsDfTime]
    listEmojis = ["📅", "📆", "🗓️"]
    listTabsLabel = [f"{listEmojis[i]} {listKeysDicts[i]}" for i in range(len(listKeysDicts))]
    listTabs = []

    if len(listKeysDicts) == 1:
        tabs1 = st.tabs(listTabsLabel)
        listTabs = [tabs1]
    elif len(listKeysDicts) == 2:
        tabs1, tabs2 = st.tabs(listTabsLabel)
        listTabs = [tabs1, tabs2]
    elif len(listKeysDicts) == 3:
        tabs1, tabs2, tabs3 = st.tabs(listTabsLabel)
        listTabs = [tabs1, tabs2, tabs3]

    for i in range(0,len(listKeysDicts),1):
        with listTabs[i]:
            general.graphDataframe(**dictParamsDfTime[listKeysDicts[i]])


    return
