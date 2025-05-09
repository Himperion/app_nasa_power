import streamlit as st
import pandas as pd
import datetime as dt
from pynasapower.get_data import query_power
from pynasapower.geometry import point
import yaml, io


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

def get_list_tabs_graph(list_data_columns: list, list_options_columns_name: list, list_options_columns_label: list):

    list_tabs_graph_name, list_tabs_graph_label = [], []
    for i in range(0,len(list_data_columns),1):
        if list_data_columns[i] in list_options_columns_name:
            list_tabs_graph_name.append(list_data_columns[i])
            list_tabs_graph_label.append(list_options_columns_label[list_options_columns_name.index(list_data_columns[i])])

    return list_tabs_graph_name, list_tabs_graph_label

def view_dataframe_information(dataframe: pd.DataFrame, dict_parameters: dict):

    listOptionsColumnsName = [dict_parameters[key]["columnLabel"] for key in dict_parameters]
    listOptionsColumnsLabel = [f"{dict_parameters[key]['emoji']} {dict_parameters[key]['columnLabel']}" for key in dict_parameters]

    list_tabs_graph_name, list_tabs_graph_label = get_list_tabs_graph(list(dataframe.columns),
                                                                      listOptionsColumnsName,
                                                                      listOptionsColumnsLabel)
     
    if len(list_tabs_graph_name) != 0:
        if len(list_tabs_graph_name) == 1:
            subtab_con1 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1[0]]
        elif len(list_tabs_graph_name) == 2:
            subtab_con1, subtab_con2 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1, subtab_con2]
        elif len(list_tabs_graph_name) == 3:
            subtab_con1, subtab_con2, subtab_con3 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1, subtab_con2, subtab_con3]
        elif len(list_tabs_graph_name) == 4:
            subtab_con1, subtab_con2, subtab_con3, subtab_con4 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1, subtab_con2, subtab_con3, subtab_con4]
        elif len(list_tabs_graph_name) == 5:
            subtab_con1, subtab_con2, subtab_con3, subtab_con4, subtab_con5 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1, subtab_con2, subtab_con3, subtab_con4, subtab_con5]
        elif len(list_tabs_graph_name) == 6:
            subtab_con1, subtab_con2, subtab_con3, subtab_con4, subtab_con5, subtab_con6 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1, subtab_con2, subtab_con3, subtab_con4, subtab_con5, subtab_con6]

        for i in range(0,len(list_subtab_con),1):
            with list_subtab_con[i]:
                st.line_chart(data=dataframe[[list_tabs_graph_name[i]]], y=list_tabs_graph_name[i])

    return

def get_bytes_yaml(dictionary: dict):

    yaml_data = yaml.dump(dictionary, allow_unicode=True)

    buffer = io.BytesIO()
    buffer.write(yaml_data.encode('utf-8'))
    buffer.seek(0)

    return buffer

def to_excel(df: pd.DataFrame):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    
    processed_data = output.getvalue()
        
    return processed_data

def name_file_head(name: str) -> str:
    now = dt.datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def viewInformation(df_data: pd.DataFrame, dict_params: dict, dict_download: dict, dict_parameters):

    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 Parámetros", "📈 Gráficas", "💾 Descargas"])

    with sub_tab1:
        with st.container(border=True):
            st.dataframe(df_data)

    with sub_tab2:
        with st.container(border=True):
            view_dataframe_information(df_data, dict_parameters)

    with sub_tab3:
        with st.container(border=True):
            for key, value in dict_download.items():
                if value['type'] == 'xlsx':
                    bytesFile = to_excel(df_data)
                elif value['type'] == 'yaml':
                    bytesFile = get_bytes_yaml(dict_params)

                st.download_button(
                    label=f"{value['emoji']} Descargar **:blue[{value['label']}] {value['type'].upper()}**",
                    data=bytesFile,
                    file_name=name_file_head(name=f"{value['fileName']}.{value['type']}"),
                    mime=value['nime'],
                    on_click="ignore")
                
    return

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
    
    viewInformation(data, dict_params, dict_download, dict_parameters)

    return