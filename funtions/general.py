import os, sys, io, yaml, calendar
import pandas as pd
import streamlit as st
import datetime as dt
from dateutil.relativedelta import relativedelta

time_info = {
    "name": "dates (Y-M-D hh:mm:ss)",
    "label": "Fecha (A-M-D hh:mm:ss)"
}

def nameFileHead(name: str) -> str:
    now = dt.datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def getBytesYaml(dictionary: dict):

    yaml_data = yaml.dump(dictionary, allow_unicode=True)
    buffer = io.BytesIO()
    buffer.write(yaml_data.encode('utf-8'))
    buffer.seek(0)

    return buffer

def toExcelResults(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")

    return output.getvalue()

def toExcelAnalysisTime(df_daily: pd.DataFrame, df_monthly: pd.DataFrame, df_annual: pd.DataFrame):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_daily.to_excel(writer, index=False, sheet_name="DailyData")
        if df_monthly is not None:
            df_monthly.to_excel(writer, index=False, sheet_name="MonthlyData")
        if df_annual is not None:
            df_annual.to_excel(writer, index=False, sheet_name="AnnualData")

    return output.getvalue()

def resource_path(relative_path: str):

    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_date_imput_nasa() -> tuple[dt.date, dt.date]:

    date_now = dt.date.today() - dt.timedelta(days=250)
    
    min_value = (date_now - relativedelta(months=1)).replace(day=1)
    max_value = min_value + relativedelta(months=1)

    return min_value, max_value

def getTimeData(df: pd.DataFrame) -> dict:

    timeInfo = {}
    numberRows = df.shape[0]

    if "dates (Y-M-D hh:mm:ss)" in df.columns:
        time_0 = df.loc[0, "dates (Y-M-D hh:mm:ss)"].to_pydatetime()
        time_1 = df.loc[1, "dates (Y-M-D hh:mm:ss)"].to_pydatetime()

        timeInfo["deltaMinutes"] = (time_1 - time_0).total_seconds()/60
        timeInfo["dateIni"] = time_0
        timeInfo["dateEnd"] = df.loc[df.index[-1], "dates (Y-M-D hh:mm:ss)"].to_pydatetime()
        timeInfo["deltaDays"] = (numberRows*timeInfo["deltaMinutes"])/1440
        timeInfo["years"] = df["dates (Y-M-D hh:mm:ss)"].dt.year.unique().tolist()

        listAuxMonth = []
        for year in timeInfo["years"]:
            df_year: pd.DataFrame = df[df["dates (Y-M-D hh:mm:ss)"].dt.year == year]

            list_month = df_year["dates (Y-M-D hh:mm:ss)"].dt.month.unique().tolist()
            listAuxMonth.append(list_month)

        timeInfo["months"] = listAuxMonth
        timeInfo["deltaMonths"] = sum([len(elm) for elm in listAuxMonth])
        timeInfo["deltaYears"] = len(timeInfo["years"])

    return timeInfo

#%% streamlit funtions

def getDownloadButtons(dictDownload: dict, df: pd.DataFrame, dictionary: dict|None):

    for _, value in dictDownload.items():
        if value["type_file"] == "xlsx":
            bytesFile = toExcelResults(df=df)
        elif value["type_file"] == "yaml":
            bytesFile = getBytesYaml(dictionary=dictionary)

        st.download_button(
            label=f"{value['emoji']} Descargar **:blue[{value['label']}] {value['type_file'].upper()}**",
            data=bytesFile,
            file_name=nameFileHead(name=f"{value['fileName']}.{value['type_file']}"),
            mime=value["nime"],
            on_click="ignore",
            key=value["key"],
            type=value["type"])
            
    return


# revisar

def get_df_load_resized(df_loadPU: pd.DataFrame, kWh_day, typeLoad):

    factor = kWh_day/df_loadPU[typeLoad].sum()
    df_load_resized = df_loadPU.copy()
    df_load_resized[f"{typeLoad} (kW)"] = df_load_resized[typeLoad]*factor

    return df_load_resized
