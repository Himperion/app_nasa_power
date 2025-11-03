import streamlit as st
import pandas as pd
import datetime as dt
from pynasapower.get_data import query_power
from pynasapower.geometry import point

from funtions import general

def get_multiselect_params(list_show_output):

    show_output = st.multiselect(label=f"🪛 **Personalizar parámetros de salida**", options=list_show_output, default=list_show_output)

    return show_output

def GMS_2_GD(dict_in):

    lat = dict_in["lat_degrees"] + (dict_in["lat_minutes"] + dict_in["lat_seconds"]/60)/60
    lon = dict_in["lon_degrees"] + (dict_in["lon_minutes"] + dict_in["lon_seconds"]/60)/60

    if dict_in["lat_NS"] == "S":
        lat = -1*lat
    if dict_in["lon_EO"] == "W":
        lon = -1*lon

    dict_params = {
        "latitude": lat,
        "longitude": lon,
        "start": dict_in["date_ini"],
        "end": dict_in["date_end"]
    }

    return dict_params

def cal_rows(date_ini, date_end, steps):

    date_delta = date_end - date_ini
    cal_rows = int((date_delta.days * 1440)/steps)

    return cal_rows

def get_parameterOptions(dict_parameters: dict) -> list:

    parameterOptions = []

    for key in dict_parameters:
        if dict_parameters[key]["NASALabel"] is not None:
            parameterOptions.append(key)

    return parameterOptions

def get_parameters_NASA_POWER(options: list, dict_parameters: dict) -> list:

    return [dict_parameters[option]["NASALabel"] for option in options]

def get_dataframe_NASA_POWER(dict_params: dict, parameters: list, dict_parameters: dict) -> pd.DataFrame:

    dataframe = query_power(geometry = point(x=dict_params["longitude"], y=dict_params["latitude"], crs="EPSG:4326"),
                            start = dict_params["start"],
                            end = dict_params["end"],
                            to_file = False,
                            community = "re",
                            parameters = parameters,
                            temporal_api = "hourly",
                            spatial_api = "point")

    list_columns, list_columns_drop = list(dataframe.columns), ["YEAR", "MO", "DY", "HR"]

    for i in range(0,len(list_columns_drop),1):
        if list_columns_drop[i] in list_columns:
            dataframe = dataframe.drop(columns=[list_columns_drop[i]])

    for key in dict_parameters:
        if dict_parameters[key]["NASALabel"] in list_columns:
            dataframe = dataframe.rename(columns={dict_parameters[key]["NASALabel"]: dict_parameters[key]["columnLabel"]})

    return dataframe

def add_column_dates(dataframe: pd.DataFrame, date_ini, rows, steps) -> pd.DataFrame:

    list_columns = list(dataframe.columns)
    if not "dates (Y-M-D hh:mm:ss)" in list_columns:
        dates = pd.date_range(start=date_ini,
                              periods=rows,
                              freq=pd.Timedelta(minutes=steps))
        
        if dataframe.shape[0] >= dates.shape[0]:
            dataframe = dataframe.head(rows)

        if dataframe.shape[0] == dates.shape[0]:
            dataframe["dates (Y-M-D hh:mm:ss)"] = dates
            dataframe = dataframe[["dates (Y-M-D hh:mm:ss)"] + list_columns]

    return dataframe

def get_outForm1(dict_params, dict_parameters, options, cal_rows):

    parameters = get_parameters_NASA_POWER(options, dict_parameters)
                    
    data = get_dataframe_NASA_POWER(dict_params, parameters, dict_parameters)
                    
    data = add_column_dates(dataframe=data, 
                            date_ini=dict_params["start"],
                            rows=cal_rows,
                            steps=60)
    
    dict_download = {
        "Xlsx": {
            "label": "Datos climaticos y potencial energético del sitio",
            "type": "xlsx",
            "fileName": "PES_params",
            "nime": "xlsx",
            "emoji": "📄"
            },
        "Yaml": {
            "label": "Archivo de datos del sitio",
            "type": "yaml",
            "fileName": "PES_data",
            "nime": "text/yaml",
            "emoji": "📌"
        }  
    }
    
    general.viewInformation(data, dict_params, dict_download)

    return