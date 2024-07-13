# -*- coding: utf-8 -*-

import folium, io, warnings
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium, folium_static
from pynasapower.get_data import query_power
from pynasapower.geometry import point, bbox
from datetime import datetime

warnings.filterwarnings("ignore")

#%% Funtions

def name_file_head(name: str) -> str:
    now = datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def cal_rows(date_ini, date_end, steps):
    date_delta = date_end - date_ini
    cal_rows = int((date_delta.days * 1440)/steps)

    return cal_rows

def get_dataframe_NASA_POWER(latitude, longitude, start, end, parameters):

    dataframe = query_power(geometry = point(x=longitude, y=latitude, crs="EPSG:4326"),
                            start = start,
                            end = end,
                            to_file = False,
                            community = "re",
                            parameters = parameters,
                            temporal_api = "hourly",
                            spatial_api = "point")

    list_columns, list_columns_drop = list(dataframe.columns), ["YEAR", "MO", "DY", "HR"]

    for i in range(0,len(list_columns_drop),1):
        if list_columns_drop[i] in list_columns:
            dataframe = dataframe.drop(columns=[list_columns_drop[i]])
        
    if "ALLSKY_SFC_SW_DWN" in list_columns:
        dataframe = dataframe.rename(columns={"ALLSKY_SFC_SW_DWN": "Gin(W/m²)"})

    return dataframe

def add_column_dates(dataframe, date_ini, rows, steps):

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

def get_list_tabs_graph(list_data_columns, list_options_columns_name, list_options_columns_label):

    list_tabs_graph_name, list_tabs_graph_label = [], []
    for i in range(0,len(list_data_columns),1):
        if list_data_columns[i] in list_options_columns_name:
            list_tabs_graph_name.append(list_data_columns[i])
            list_tabs_graph_label.append(list_options_columns_label[list_options_columns_name.index(list_data_columns[i])])

    return list_tabs_graph_name, list_tabs_graph_label

def view_dataframe_information(dataframe):
    list_options_columns_name = ["Load(W)", "Gin(W/m²)", "Tamb(°C)", "Vwind(m/s)"]
    list_options_columns_label = ["💡 Load(W)", "🌤️ Gin(W/m²)", "🌡️ Tamb(°C)", "✈️ Vwind(m/s)"]
    list_data_columns = list(dataframe.columns)

    list_tabs_graph_name, list_tabs_graph_label = get_list_tabs_graph(list_data_columns,
                                                                      list_options_columns_name,
                                                                      list_options_columns_label)
    
    tab_con1, tab_con2 = st.tabs(["📄 Tabla", "📈 Gráficas"])
    with tab_con1:
        st.dataframe(dataframe)
    with tab_con2: 
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

            for i in range(0,len(list_subtab_con),1):
                with list_subtab_con[i]:
                    st.line_chart(data=dataframe[[list_tabs_graph_name[i]]], y=list_tabs_graph_name[i])

    return

#%% Session_state

if 'app_1_option_1_var_flagAccept' not in st.session_state:
    st.session_state.app_1_option_1_var_flagAccept = False

#%% Main

st.header(":mostly_sunny: All Sky Surface Shortwave Downward Irradiance", divider=True)

with st.form("app_1_option_1"):
    data_dates = ""

    col1, col2 = st.columns( [0.5, 0.5])

    lat_input = col1.number_input('Ingrese la latitud:', min_value=-90.0, max_value=90.0, step=0.000001, format="%.6f", value=7.142056)
    lon_input = col2.number_input('Ingrese la longitud:', min_value=-180.0, max_value=180.0, step=0.000001, format="%.6f", value=-73.121231)

    date_ini = col1.date_input("Fecha de inicio:")
    date_end = col2.date_input("Fecha Final:")

    m = folium.Map(location=[lat_input, lon_input], zoom_start=17)

    folium.Marker([lat_input, lon_input],
                  popup=f'Latitud: {lat_input}, Longitud: {lon_input}',
                  draggable=False).add_to(m)

    st_data = st_folium(m, width=725, height=400)

    app_1_option_1_submitted = st.form_submit_button("Aceptar")

    if app_1_option_1_submitted:
        cal_rows = cal_rows(date_ini, date_end, steps=60)

        if cal_rows > 0:
            data = get_dataframe_NASA_POWER(latitude=lat_input,
                                            longitude=lon_input,
                                            start=date_ini,
                                            end=date_end,
                                            parameters=["ALLSKY_SFC_SW_DWN"])
                    
            data_dates = add_column_dates(dataframe=data,
                                          date_ini=date_ini,
                                          rows=cal_rows,
                                          steps=60)
            
            with st.container(border=True):
                view_dataframe_information(data_dates)

            st.session_state.app_1_option_1_var_flagAccept = True

if st.session_state.app_1_option_1_var_flagAccept and isinstance(data_dates, pd.DataFrame):
            
            
    excel_bytes_io = io.BytesIO()
    data_dates.to_excel(excel_bytes_io, index=False)
    excel_bytes_io.seek(0)

    st.download_button(label="Descargar archivo",
                       data= excel_bytes_io.read(),
                       file_name=name_file_head("ALLSKY_SFC_SW_DWN.xlsx"))

