import pandas as pd
import plotly.express as px
import streamlit as st

from funtions import general, timeSteps, heatmaps, windRose, solarCard
from data.param import DICT_PARAMS, DICT_PARAMS_LABEL_KEY, DICT_PARAMS_WIND, DICT_TIME

CONFIG_PX ={
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "zoom", "pan", "hoverClosestCartesian", "hoverCompareCartesian",
        "sendDataToCloud", "zoomIn", "zoomOut", "lasso2d", "select2d",
        "autoscale", "resetScale2d"]
}

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
    if "SUN_AZMT" in listColumnsKeys and "SUN_ELVT" in listColumnsKeys:
        listColumnsKeys = fixListColumnsKey(listColumnsKeys, remove_wd="SUN_AZMT", remove_ws="SUN_ELVT", add_w="SOLAR-CHART")

    for item in listColumnsKeys:
        listColumnsLabel.append(DICT_PARAMS[item]["Label"])
        listColumnsTabs.append(f"{DICT_PARAMS[item]['Emoji']} {DICT_PARAMS[item]['Label']}")

    return listColumnsKeys, listColumnsLabel, listColumnsTabs

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

def viweDfInfoTime(df: pd.DataFrame, timeInfo: dict, column_label: str, rangeSelector=True, rangeSlider=True):

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
        st.plotly_chart(fig, config=CONFIG_PX)

    return

def viewTabWind(df: pd.DataFrame, key: str, timeInfo: dict):

    ws_key, wd_key = DICT_PARAMS_WIND[key]["WS"], DICT_PARAMS_WIND[key]["WD"]
    ws_label, wd_label = DICT_PARAMS[ws_key]["Label"], DICT_PARAMS[wd_key]["Label"]
    ws_name, ws_color = DICT_PARAMS[ws_key]["Name"], DICT_PARAMS[wd_key]["Color"]
    
    wind_df = windRose.make_wind_df(data_df=df, ws_label=ws_label, wd_label=wd_label)
    color_discrete_map = windRose.get_colors_of_strength(wind_df)

    tab1, tab2, tab3 = st.tabs([":material/bid_landscape: Gráfica de tiempo ", ":material/explore: Dirección del viento", ":material/speed: Velocidad del viento"])

    with tab1:
        viewSummaryMetrics(df=df, column_label=ws_label, column_unit=DICT_PARAMS[ws_key]["Unit"])
        viweDfInfoTime(df=df, timeInfo=timeInfo, column_label=ws_label)
    with tab2:
        windRose.plotly_windrose(wind_df=wind_df, color_discrete_map=color_discrete_map, config=CONFIG_PX, column_name=ws_name)
        windRose.plotly_windhist(wind_df=wind_df, color_discrete_map=color_discrete_map, config=CONFIG_PX, column_name=ws_name)

        dictWindDownload = {
            "Xlsx": {
                "label": "Datos histograma de velocidad del viento",
                "type_file": "xlsx",
                "fileName": f"PES_histWind_{key}",
                "nime": "xlsx",
                "emoji": ":material/description:",
                "key": f"PES_histWind_{key}",
                "type": "secondary"
            }
        }

        general.getDownloadButtons(dictDownload=dictWindDownload, df=wind_df, dictionary=None)
    with tab3:
        tab3sub1, tab3sub2 = st.tabs([":material/bar_chart: Histograma", ":material/mode_heat: Heatmaps"])

        with tab3sub1:
            windRose.plotly_histWS(df=df, ws_key=ws_key, ws_label=ws_label, ws_name=ws_name, ws_color=ws_color, config=CONFIG_PX)
        with tab3sub2:
            heatmaps.get_heatmaps(df=df, timeInfoYears=timeInfo["years"], Label=ws_label, Name=ws_name, config_PX=CONFIG_PX)
        
    return

def viewTabSolarProjection(df: pd.DataFrame):
     
    sub_tab1, sub_tab2 = st.tabs([":material/explore: Proyección Estereográfica", "Proyección Cilíndrica"])

    with sub_tab1:
        solarCard.plotlySolarProjection(df)
    with sub_tab2:
        solarCard.plotyCylindricalProjection(df)
     
    return

def viewSummaryMetrics(df: pd.DataFrame, column_label: str, column_unit: str):

    mean = round(df[column_label].mean(), 2)
    max = round(df[column_label].max(), 2)
    min = round(df[column_label].min(), 2)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Promedio",
            value=mean,
            icon=":material/functions:",
            border=True,
            delta=column_unit,
            delta_arrow="off",
            delta_color="off"
        )
    with col2:
        st.metric(
            label="Máximo",
            value=max,
            icon=":material/expand_circle_up:",
            border=True,
            delta=column_unit,
            delta_arrow="off",
            delta_color="off"
        )
    with col3:
        st.metric(
            label="Mínimo",
            value=min,
            icon=":material/expand_circle_down:",
            border=True,
            delta=column_unit,
            delta_arrow="off",
            delta_color="off"
        )

    return

def viewDfInfo(df: pd.DataFrame):

    listColumnsKeys, listColumnsLabel, listColumnsTabs = getListsTabsGraph(listDfColumns=df)
    timeInfo = general.getTimeData(df)
    df_day, df_month, df_year = None, None, None

    listSubTabCon = list(st.tabs(listColumnsTabs))

    if "ALLSKY_SFC_SW_DWN" in listColumnsKeys or "LOAD" in listColumnsKeys:
        df_day, df_month, df_year = timeSteps.getDfsTimeLapse(df=df, timeInfo=timeInfo)
       
    for i in range(0,len(listColumnsKeys),1):
        columnKey = listColumnsKeys[i]
        with listSubTabCon[i]:
            if columnKey == "ALLSKY_SFC_SW_DWN" or columnKey == "LOAD":
                tab1, tab2, tab3 = st.tabs([":material/bid_landscape: Gráfica de tiempo ", ":material/finance: Diagrama de barras", ":material/mode_heat: Heatmaps"])
                with tab1:
                    viewSummaryMetrics(df=df, column_label=listColumnsLabel[i], column_unit=DICT_PARAMS[columnKey]["Unit"])
                    viweDfInfoTime(df=df, timeInfo=timeInfo, column_label=listColumnsLabel[i])
                with tab2:    
                    timeSteps.viewDfsTimeLapse(columnKey, df_day, df_month, df_year, timeInfo)
                with tab3:
                    heatmaps.get_heatmaps(df=df, timeInfoYears=timeInfo["years"], Label=DICT_PARAMS[columnKey]["Label"], Name=DICT_PARAMS[columnKey]["Name"], config_PX=CONFIG_PX)
                    
            elif  listColumnsKeys[i] == "W10M" or listColumnsKeys[i] == "W50M":
                viewTabWind(df=df,  key=listColumnsKeys[i], timeInfo=timeInfo)
            elif listColumnsKeys[i] == "SOLAR-CHART":
                viewTabSolarProjection(df=df)
            else:
                viewSummaryMetrics(df=df, column_label=listColumnsLabel[i], column_unit=DICT_PARAMS[columnKey]["Unit"])
                viweDfInfoTime(df=df, timeInfo=timeInfo, column_label=listColumnsLabel[i])
                
    return df_day, df_month, df_year


def viewInformation(df_data: pd.DataFrame, dict_params: dict|None, dict_download: dict):

    df_day, df_month, df_year = None, None, None

    sub_tab1, sub_tab2, sub_tab3 = st.tabs([":material/grid_on: Parámetros", ":material/bid_landscape: Gráficas", ":material/save: Descargas"])

    with sub_tab1:
        with st.container(border=True):
            st.dataframe(df_data)
    with sub_tab2:
        with st.container(border=True):
            df_day, df_month, df_year = viewDfInfo(df_data)
    with sub_tab3:
        with st.container(border=True):
            general.getDownloadButtons(dictDownload=dict_download, df=df_data, dictionary=dict_params)

            if df_day is not None and (df_month is not None or df_year is not None):
                bytesFile = general.toExcelAnalysisTime(df_day, df_month, df_year)

                st.download_button(
                    label=":material/file_save: Descargar **:blue[Datos en estampas de tiempo] XLSX**",
                    data=bytesFile,
                    file_name=general.nameFileHead(name="dataTimeStamps.xlsx"),
                    mime="xlsx",
                    on_click="ignore",
                    type="secondary"
                )
  
    return

def graphDataframe(df: pd.DataFrame, x, y, color, value_label, title, timeInfo: dict|None=None, rangeSelector=False, rangeSlider=False, Unit: str|None=None):

    dict_xaxis = getDictRangeSelectorSlider(timeInfo=timeInfo, rangeSelector=rangeSelector, rangeSlider=rangeSlider)

    fig = px.bar(df, x=x, y=y, color_discrete_sequence=[color], labels={y: value_label}, title=title)
    
    fig.update_layout(
        xaxis_tickangle=0,
        xaxis=dict_xaxis
    )

    with st.container(border=True):
        st.plotly_chart(fig, config=CONFIG_PX)

    return