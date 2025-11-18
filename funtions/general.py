import os, sys, io, yaml, calendar
import pandas as pd
import streamlit as st
import datetime as dt
import plotly.express as px

from funtions import windRose, timeSteps, heatmaps
from data.param import DICT_PARAMS, DICT_PARAMS_LABEL_KEY, DICT_PARAMS_WIND, DICT_TIME

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
    min_value = date_now.replace(day=1, month=date_now.month-1)
    max_value = min_value.replace(month=min_value.month+1)

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

def getRangeSelector(timeInfo: dict) -> list:

    range_selector = []

    if timeInfo["deltaDays"] >= 7:
        range_selector.append(dict(count=7, label="1S", step="day", stepmode="backward"))
    if timeInfo["deltaMonths"] >= 1:
        range_selector.append(dict(count=1, label="1M", step="month", stepmode="backward"))
    if timeInfo["deltaMonths"] >= 6:
        range_selector.append(dict(count=6, label="6M", step="month", stepmode="backward"))
    if timeInfo["deltaYears"] >= 1:
        range_selector.append(dict(count=1, label="1A", step="year", stepmode="backward"))

    range_selector.append(dict(step="all", label="MAX."))

    return list(range_selector)

def fixListColumnsKey(listFix: list, remove_wd: str, remove_ws: str, add_w: str) -> list:

    listFix.remove(remove_wd)
    listFix.remove(remove_ws)
    listFix.append(add_w)

    return listFix

def getListsTabsGraph(listDfColumns: list) -> tuple[list, list, list]:

    listParamsLabel = list(DICT_PARAMS_LABEL_KEY.keys())
    listColumnsKeys = [DICT_PARAMS_LABEL_KEY[item] for item in listDfColumns if item in listParamsLabel]
    listColumnsLabel, listColumnsTabs = [], []

    if "WD10M" in listColumnsKeys and "WS10M" in listColumnsKeys:
        listColumnsKeys = fixListColumnsKey(listColumnsKeys, remove_wd="WD10M", remove_ws="WS10M", add_w="W10M")
    if "WD50M" in listColumnsKeys and "WS50M" in listColumnsKeys:
        listColumnsKeys = fixListColumnsKey(listColumnsKeys, remove_wd="WD50M", remove_ws="WS50M", add_w="W50M")

    for item in listColumnsKeys:
        listColumnsLabel.append(DICT_PARAMS[item]["Label"])
        listColumnsTabs.append(f"{DICT_PARAMS[item]['Emoji']} {DICT_PARAMS[item]['Label']}")

    return listColumnsKeys, listColumnsLabel, listColumnsTabs

def getDictRangeSelectorSlider(timeInfo: dict|None, rangeSelector: bool, rangeSlider: bool) -> dict:

    dict_range_selector, dict_range_slider = {}, {}
    
    if rangeSelector and timeInfo is not None:
        range_selector = getRangeSelector(timeInfo=timeInfo)
        dict_range_selector = dict(
            rangeselector=dict(buttons=range_selector)
        )
    if rangeSlider:
        dict_range_slider = dict(
            rangeslider=dict(visible=True)
        )

    return {**dict(showgrid=True),**dict_range_selector, **dict_range_slider}

def graphDataframe(df: pd.DataFrame, x, y, color, value_label, title, timeInfo: dict|None=None, rangeSelector=False, rangeSlider=False):

    dict_xaxis = getDictRangeSelectorSlider(timeInfo=timeInfo, rangeSelector=rangeSelector, rangeSlider=rangeSlider)

    fig = px.bar(df, x=x, y=y, color_discrete_sequence=[color], labels={y: value_label}, title=title)
    
    fig.update_layout(
        xaxis_tickangle=0,
        xaxis=dict_xaxis
    )

    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, config=CONFIG_PX)

    return

def viwe_info_df_time(df: pd.DataFrame, timeInfo: dict, column_label: str, rangeSelector=True, rangeSlider=True):

    key = DICT_PARAMS_LABEL_KEY[column_label]
    
    fig = px.line(df, x="dates (Y-M-D hh:mm:ss)", y=column_label,
                  labels={
                        "dates (Y-M-D hh:mm:ss)": DICT_TIME["dates (Y-M-D hh:mm:ss)"]["Name"],
                        column_label: DICT_PARAMS[key]["Name"]
                  },
                  title=DICT_PARAMS[key]["Name"])
    
    dict_xaxis = getDictRangeSelectorSlider(timeInfo=timeInfo, rangeSelector=rangeSelector, rangeSlider=rangeSlider)

    fig.update_layout(xaxis=dict_xaxis)
    fig.update_traces(line_color=DICT_PARAMS[key]["Color"])

    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, config=CONFIG_PX)

    return

def viewDataframeWind(df: pd.DataFrame, key: str, timeInfo: dict):

    ws_key, wd_key = DICT_PARAMS_WIND[key]["WS"], DICT_PARAMS_WIND[key]["WD"]
    ws_label, wd_label = DICT_PARAMS[ws_key]["Label"], DICT_PARAMS[wd_key]["Label"]
    ws_name, ws_color = DICT_PARAMS[ws_key]["Name"], DICT_PARAMS[wd_key]["Color"]
    
    wind_df = windRose.make_wind_df(data_df=df, ws_label=ws_label, wd_label=wd_label)
    color_discrete_map = windRose.get_colors_of_strength(wind_df)

    tab1, tab2, tab3 = st.tabs(["📈 Gráfica de tiempo ", "🧭 Dirección del viento", "🏃 Velocidad del viento"])

    with tab1:
        viwe_info_df_time(df=df, timeInfo=timeInfo, column_label=ws_label)
    with tab2:
        windRose.plotly_windrose(wind_df=wind_df, color_discrete_map=color_discrete_map, config=CONFIG_PX, column_name=ws_name)
        windRose.plotly_windhist(wind_df=wind_df, color_discrete_map=color_discrete_map, config=CONFIG_PX, column_name=ws_name)

        dictWindDownload = {
            "Xlsx": {
                "label": "Datos histograma de velocidad del viento",
                "type_file": "xlsx",
                "fileName": f"PES_histWind_{key}",
                "nime": "xlsx",
                "emoji": "📄",
                "key": f"PES_histWind_{key}",
                "type": "secondary"
            }
        }

        getDownloadButtons(dictDownload=dictWindDownload, df=wind_df, dictionary=None)
    with tab3:
        windRose.plotly_histWS(df=df, ws_key=ws_key, ws_label=ws_label, ws_name=ws_name, ws_color=ws_color, config=CONFIG_PX)
        

    return

def view_dataframe_information(df: pd.DataFrame):

    listColumnsKeys, listColumnsLabel, listColumnsTabs = getListsTabsGraph(listDfColumns=df)
    timeInfo = getTimeData(df)
    listSubTabCon = []
    df_day, df_month, df_year = None, None, None
    
    if len(listColumnsTabs) == 1:
        subtab_con1 = st.tabs(listColumnsTabs)
        listSubTabCon = [subtab_con1[0]]
    elif len(listColumnsTabs) == 2:
        subtab_con1, subtab_con2 = st.tabs(listColumnsTabs)
        listSubTabCon = [subtab_con1, subtab_con2]
    elif len(listColumnsTabs) == 3:
        subtab_con1, subtab_con2, subtab_con3 = st.tabs(listColumnsTabs)
        listSubTabCon = [subtab_con1, subtab_con2, subtab_con3]
    elif len(listColumnsTabs) == 4:
        subtab_con1, subtab_con2, subtab_con3, subtab_con4 = st.tabs(listColumnsTabs)
        listSubTabCon = [subtab_con1, subtab_con2, subtab_con3, subtab_con4]
    elif len(listColumnsTabs) == 5:
        subtab_con1, subtab_con2, subtab_con3, subtab_con4, subtab_con5 = st.tabs(listColumnsTabs)
        listSubTabCon = [subtab_con1, subtab_con2, subtab_con3, subtab_con4, subtab_con5]

    if "ALLSKY_SFC_SW_DWN" in listColumnsKeys or "LOAD" in listColumnsKeys:
        df_day, df_month, df_year = timeSteps.getDfsTimeLapse(df=df, timeInfo=timeInfo)


        # heatmap
        # if "ALLSKY_SFC_SW_DWN" in listColumnsKeys:
        #     for year in timeInfo["years"]:
       

    for i in range(0,len(listColumnsKeys),1):
        columnKey = listColumnsKeys[i]
        with listSubTabCon[i]:
            if columnKey == "ALLSKY_SFC_SW_DWN" or columnKey == "LOAD":
                tab1, tab2, tab3 = st.tabs(["📈 Gráfica de tiempo ", f"📊 Diagrama de barras", "🔥 Heatmaps"])
                with tab1:
                    viwe_info_df_time(df=df, timeInfo=timeInfo, column_label=listColumnsLabel[i])
                with tab2:    
                    timeSteps.viewDfsTimeLapse(columnKey, df_day, df_month, df_year, timeInfo)
                with tab3:
                    heatmaps.get_heatmaps(df=df, timeInfoYears=timeInfo["years"], Label=DICT_PARAMS[columnKey]["Label"], Name=DICT_PARAMS[columnKey]["Name"], config_PX=CONFIG_PX)
                    
            elif  listColumnsKeys[i] == "W10M" or listColumnsKeys[i] == "W50M":
                viewDataframeWind(df=df,  key=listColumnsKeys[i], timeInfo=timeInfo)        
            else:
                viwe_info_df_time(df=df, timeInfo=timeInfo, column_label=listColumnsLabel[i])
                
    return df_day, df_month, df_year

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

def viewInformation(df_data: pd.DataFrame, dict_params: dict|None, dict_download: dict):

    df_day, df_month, df_year = None, None, None

    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 Parámetros", "📈 Gráficas", "💾 Descargas"])

    with sub_tab1:
        with st.container(border=True):
            st.dataframe(df_data)
    with sub_tab2:
        with st.container(border=True):
            df_day, df_month, df_year = view_dataframe_information(df_data)
    with sub_tab3:
        with st.container(border=True):
            getDownloadButtons(dictDownload=dict_download, df=df_data, dictionary=dict_params)

            if df_day is not None and (df_month is not None or df_year is not None):
                bytesFile = toExcelAnalysisTime(df_day, df_month, df_year)

                st.download_button(
                    label="📄 Descargar **:blue[Datos en estampas de tiempo] XLSX**",
                    data=bytesFile,
                    file_name=nameFileHead(name="dataTimeStamps.xlsx"),
                    mime="xlsx",
                    on_click="ignore",
                    type="secondary"
                )
  
    return

# revisar

def get_df_load_resized(df_loadPU: pd.DataFrame, kWh_day, typeLoad):

    factor = kWh_day/df_loadPU[typeLoad].sum()
    df_load_resized = df_loadPU.copy()
    df_load_resized[f"{typeLoad} (kW)"] = df_load_resized[typeLoad]*factor

    return df_load_resized
