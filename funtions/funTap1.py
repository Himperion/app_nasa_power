import streamlit as st
import pandas as pd
import datetime as dt
from pynasapower.get_data import query_power
from pynasapower.geometry import point

from funtions import general

dict_download = {
    "Xlsx": {
        "label": "Datos climaticos y potencial energético del sitio",
        "type_file": "xlsx",
        "fileName": "PES_params",
        "nime": "xlsx",
        "emoji": "📄",
        "key": "PES_params",
        "type": "primary"
        },
    "Yaml": {
        "label": "Archivo de datos del sitio",
        "type_file": "yaml",
        "fileName": "PES_data",
        "nime": "text/yaml",
        "emoji": "📌",
        "key": "PES_data",
        "type": "secondary"
    }  
}

selectDataEntryOptions = [
    "🗺️ Mapa interactivo",
    "📌 Datos del sitio",
    "💾 Cargar archivo de datos del sitio YAML"
    ]

selectCoordinateOptions = [
    "Sistema sexagesimal GMS",
    "Sistema decimal GD"
    ]

def get_multiselect_params(list_show_output):

    show_output = st.multiselect(label=f"🪛 **Personalizar parámetros de salida**", options=list_show_output, default=list_show_output)

    return show_output

def GMS_2_GD(dict_in):

    latitude = dict_in["lat_degrees"] + (dict_in["lat_minutes"] + dict_in["lat_seconds"]/60)/60
    longitude = dict_in["lon_degrees"] + (dict_in["lon_minutes"] + dict_in["lon_seconds"]/60)/60

    if dict_in["NS"] == "S":
        latitude = -1*latitude
    if dict_in["EO"] == "W":
        longitude = -1*longitude

    return latitude, longitude

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

def get_out(dict_params, dict_parameters, options, cal_rows):

    parameters = get_parameters_NASA_POWER(options, dict_parameters)      
    data = get_dataframe_NASA_POWER(dict_params, parameters, dict_parameters)     
    data = add_column_dates(dataframe=data, date_ini=dict_params["start"], rows=cal_rows, steps=60)

    return data

def get_outForm1(dict_params, dict_parameters, options, cal_rows):

    parameters = get_parameters_NASA_POWER(options, dict_parameters)            
    data = get_dataframe_NASA_POWER(dict_params, parameters, dict_parameters)      
    data = add_column_dates(dataframe=data, date_ini=dict_params["start"], rows=cal_rows, steps=60)
    
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

#%% streamlit funtions

def get_number_input_degrees_minutes_seconds(type: str, value: tuple, border: bool):

    lat_lon = None

    with st.container(border=border):
        col1, col2, col3, col4 = st.columns(4)

        if type == "lat":
            lat_lon = col1.selectbox("**Latitud:**", ["N", "S"], index=0)
        elif type == "lng":
            lat_lon = col1.selectbox("**Longitud:**", ["W", "E"], index=0)
        
        degrees = col2.number_input(label="Grados", min_value=0, value=value[0])
        minutes = col3.number_input(label="Minutos", min_value=0, value=value[1])
        seconds = col4.number_input(label="Segundos", min_value=0.0, format="%.4f", value=value[2])
        
    return lat_lon, degrees, minutes, seconds

def get_GMS_2_GD():

    NS, lat_degrees, lat_minutes, lat_seconds = get_number_input_degrees_minutes_seconds(type="lat", value=(7, 8, 31.4016), border=True)
    EO, lon_degrees, lon_minutes, lon_seconds = get_number_input_degrees_minutes_seconds(type="lng", value=(73, 7, 16.4316), border=True)

    latitude, longitude = GMS_2_GD({
        "NS": NS, "lat_degrees": lat_degrees, "lat_minutes": lat_minutes, "lat_seconds": lat_seconds,
        "EO": EO, "lon_degrees": lon_degrees, "lon_minutes": lon_minutes, "lon_seconds": lon_seconds
    })

    return latitude, longitude

def get_number_input_latitude_longitude(lat_value: float, lon_value: float):

    col1, col2 = st.columns(2)
    lat_input = col1.number_input('Ingrese la latitud:', min_value=-90.0, max_value=90.0, step=0.000001, format="%.6f", value=lat_value)
    lon_input = col2.number_input('Ingrese la longitud:', min_value=-180.0, max_value=180.0, step=0.000001, format="%.6f", value=lon_value)

    return lat_input, lon_input






col1, col2 = st.columns(2)

