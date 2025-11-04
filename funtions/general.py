import os, sys, io, yaml, calendar
import pandas as pd
import streamlit as st
import datetime as dt
import plotly.express as px

from funtions import windRose
from data.param import DICT_PARAMS_NAME, DICT_PARAMS_LABEL, DICT_NASA_LABEL

CONFIG_PX ={
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["zoom", "pan", "hoverClosestCartesian", "hoverCompareCartesian",
                                   "sendDataToCloud", "zoomIn", "zoomOut", "lasso2d", "select2d",
                                   "autoscale", "resetScale2d"]
    }

time_info = {
    "name": "dates (Y-M-D hh:mm:ss)",
    "label": "Fecha (A-M-D hh:mm:ss)"
}

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

def resource_path(relative_path: str):

    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def name_file_head(name: str) -> str:
    now = dt.datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def get_date_imput_nasa() -> tuple[dt.date, dt.date]:

    date_now = dt.date.today() - dt.timedelta(days=250)
    min_value = date_now.replace(day=1, month=date_now.month-1)
    max_value = min_value.replace(month=min_value.month+1)

    return min_value, max_value

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

def get_range_selector(df: pd.DataFrame, column_date: str) -> list:

    range_days = (df[column_date].max() - df[column_date].min()).days
    range_selector = []

    if range_days > 1:
        range_selector.append(dict(count=1, label="1D", step="day", stepmode="backward"))
    if range_days > 6:
        range_selector.append(dict(count=7, label="1S", step="day", stepmode="backward"))
    if range_days > 29:
        range_selector.append(dict(count=1, label="1M", step="month", stepmode="backward"))
    if range_days > 180:
        range_selector.append(dict(count=6, label="6M", step="month", stepmode="backward"))
    if range_days > 364:
        range_selector.append(dict(count=1, label="1A", step="year", stepmode="backward"))

    range_selector.append(dict(step="all", label="MAX."))

    return list(range_selector)

def get_list_tabs_graph_name(list_df_columns: list) -> tuple[list, list]:

    list_columns_tabs = []

    list_params_label = list(DICT_PARAMS_LABEL.keys())
    list_columns_label = [item for item in list_df_columns if item in list_params_label]

    if DICT_NASA_LABEL["WD10M"] in list_columns_label and DICT_NASA_LABEL["WS10M"] in list_columns_label:
        list_columns_label.remove(DICT_NASA_LABEL["WD10M"])
        list_columns_label.remove(DICT_NASA_LABEL["WS10M"])
        list_columns_label.append("Wind 10m")

    if DICT_NASA_LABEL["WD50M"] in list_columns_label and DICT_NASA_LABEL["WS50M"] in list_columns_label:
        list_columns_label.remove(DICT_NASA_LABEL["WD50M"])
        list_columns_label.remove(DICT_NASA_LABEL["WS50M"])
        list_columns_label.append("Wind 50m")

    for item in list_columns_label:
        if item in list_params_label:
            list_columns_tabs.append(f"{DICT_PARAMS_LABEL[item]['emoji']} {item}")
        elif item == "Wind 10m" or item == "Wind 50m":
            list_columns_tabs.append(f"🪁 {item}")

    return list_columns_label, list_columns_tabs

def get_dict_range_selector_slider(df: pd.DataFrame, column_date: str, rangeSelector: bool, rangeSlider: bool) -> dict:

    dict_range_selector, dict_range_slider = {}, {}
    
    if rangeSelector:
        range_selector = get_range_selector(df=df, column_date=column_date)
        dict_range_selector = dict(
            rangeselector=dict(buttons=range_selector)
        )
    if rangeSlider:
        dict_range_slider = dict(
            rangeslider=dict(visible=True)
        )

    return {**dict(type="date"), **dict(showgrid=True),**dict_range_selector, **dict_range_slider}

def graph_dataframe(df: pd.DataFrame, x, y, color, value_label, title, rangeSelector=False, rangeSlider=False):

    dict_xaxis = get_dict_range_selector_slider(df=df, column_date=x, rangeSelector=rangeSelector, rangeSlider=rangeSlider)

    fig = px.bar(df, x=x, y=y, color_discrete_sequence=[color], labels={y: value_label}, title=title)
    
    fig.update_layout(
        xaxis_tickangle=0,
        xaxis=dict_xaxis,
        yaxis=dict(tickformat=".3f", showgrid=True)
    )

    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, config=CONFIG_PX)

    return

def viwe_info_df_time(df: pd.DataFrame, column_date: str, column_label: str, rangeSelector=True, rangeSlider=True):
    
    fig = px.line(df, x="dates (Y-M-D hh:mm:ss)", y=column_label,
                  labels={
                        time_info["name"]: time_info["label"],
                        column_label: DICT_PARAMS_LABEL[column_label]["name"]
                  },
                  title=DICT_PARAMS_LABEL[column_label]["name"])
    
    dict_xaxis = get_dict_range_selector_slider(df=df, column_date=column_date, rangeSelector=rangeSelector, rangeSlider=rangeSlider)

    fig.update_layout(xaxis=dict_xaxis)
    fig.update_traces(line_color=DICT_PARAMS_LABEL[column_label]["color"])

    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, config=CONFIG_PX)

    return

def get_df_psh(df: pd.DataFrame, delta_minutes, column_label: str) -> pd.DataFrame:

    list_psh, list_date = [], []

    delta_t = delta_minutes/60
    samples = int((1/delta_t)*24)

    for i in range(0,int(df.shape[0]/samples),1):
        lowerValue, upperValue = samples*i, samples*(i+1)-1

        psh = round((df.loc[lowerValue:upperValue, column_label].sum()*delta_t)/1000, 2)
        list_psh.append(psh)

        date = df.loc[lowerValue, "dates (Y-M-D hh:mm:ss)"].date()
        list_date.append(date)

    df_out = pd.DataFrame({
        "Fecha (Y-M-D)": list_date,
        "HSP": list_psh
    })

    return df_out

def view_dataframe_information(dataframe: pd.DataFrame):

    list_df_columns = list(dataframe.columns)
    list_columns_label, list_columns_tabs = get_list_tabs_graph_name(list_df_columns)
    time_info = getTimeData(dataframe)
    
    if len(list_columns_tabs) == 1:
        subtab_con1 = st.tabs(list_columns_tabs)
        list_subtab_con = [subtab_con1[0]]
    elif len(list_columns_tabs) == 2:
        subtab_con1, subtab_con2 = st.tabs(list_columns_tabs)
        list_subtab_con = [subtab_con1, subtab_con2]
    elif len(list_columns_tabs) == 3:
        subtab_con1, subtab_con2, subtab_con3 = st.tabs(list_columns_tabs)
        list_subtab_con = [subtab_con1, subtab_con2, subtab_con3]
    elif len(list_columns_tabs) == 4:
        subtab_con1, subtab_con2, subtab_con3, subtab_con4 = st.tabs(list_columns_tabs)
        list_subtab_con = [subtab_con1, subtab_con2, subtab_con3, subtab_con4]
    elif len(list_columns_tabs) == 5:
        subtab_con1, subtab_con2, subtab_con3, subtab_con4, subtab_con5 = st.tabs(list_columns_tabs)
        list_subtab_con = [subtab_con1, subtab_con2, subtab_con3, subtab_con4, subtab_con5]

    for i in range(0,len(list_columns_label),1):
        with list_subtab_con[i]:
            if list_columns_label[i] != "Wind 10m" and list_columns_label[i] != "Wind 50m":
                viwe_info_df_time(dataframe, column_date="dates (Y-M-D hh:mm:ss)", column_label=list_columns_label[i])

                if DICT_PARAMS_LABEL[list_columns_label[i]]["NASALabel"] == "ALLSKY_SFC_SW_DWN":
                    #viwe_info_df_HSP(dataframe, time_info, column_label=list_columns_label[i])

                    df_psh = get_df_psh(df=dataframe, delta_minutes=time_info["deltaMinutes"], column_label=list_columns_label[i])

                    st.text(DICT_PARAMS_LABEL[list_columns_label[i]]["color"])

                    

                    graph_dataframe(df=df_psh, x="Fecha (Y-M-D)", y="HSP", color=DICT_PARAMS_LABEL[list_columns_label[i]]["color"],
                                    value_label="Hora Solar Pico", title="Hora Solar Pico (HSP)", rangeSelector=True)

                    #st.dataframe(df_psh)
            else:
                if list_columns_label[i] == "Wind 10m":
                    wind_df_10 = windRose.make_wind_df(data_df=dataframe, ws_label=DICT_NASA_LABEL["WS10M"], wd_label=DICT_NASA_LABEL["WD10M"])
                    color_discrete_map = windRose.get_colors_of_strength(wind_df_10)
                    column_name = DICT_PARAMS_LABEL[DICT_NASA_LABEL["WS10M"]]["name"]

                    tab1, tab2, tab3 = st.tabs(["📈 Gráfica de tiempo ", "🌬️ Rosa de los vientos", "📊 Histograma"])

                    with tab1:
                        viwe_info_df_time(dataframe, column_date="dates (Y-M-D hh:mm:ss)", column_label=DICT_NASA_LABEL["WS10M"])
                    with tab2:
                        windRose.plotly_windrose(wind_df=wind_df_10, color_discrete_map=color_discrete_map, config=CONFIG_PX, column_name=column_name)
                    with tab3:
                        windRose.plotly_windhist(wind_df=wind_df_10, color_discrete_map=color_discrete_map, config=CONFIG_PX, column_name=column_name)

                elif list_columns_label[i] == "Wind 50m":
                    wind_df_50 = windRose.make_wind_df(data_df=dataframe, ws_label=DICT_NASA_LABEL["WS50M"], wd_label=DICT_NASA_LABEL["WD50M"])
                    color_discrete_map = windRose.get_colors_of_strength(wind_df_50)
                    column_name = DICT_PARAMS_LABEL[DICT_NASA_LABEL["WS50M"]]["name"]

                    tab1, tab2, tab3 = st.tabs(["📈 Gráfica de tiempo ", "🌬️ Rosa de los vientos", "📊 Histograma"])

                    with tab1:
                        viwe_info_df_time(dataframe, column_date="dates (Y-M-D hh:mm:ss)", column_label=DICT_NASA_LABEL["WS50M"])
                    with tab2:
                        windRose.plotly_windrose(wind_df=wind_df_50, color_discrete_map=color_discrete_map, config=CONFIG_PX, column_name=column_name)
                    with tab3:
                        windRose.plotly_windhist(wind_df=wind_df_50, color_discrete_map=color_discrete_map, config=CONFIG_PX, column_name=column_name)
 
    return

def viewInformation(df_data: pd.DataFrame, dict_params: dict, dict_download: dict):

    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 Parámetros", "📈 Gráficas", "💾 Descargas"])

    with sub_tab1:
        with st.container(border=True):
            st.dataframe(df_data)

    with sub_tab2:
        with st.container(border=True):
            view_dataframe_information(df_data)

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
