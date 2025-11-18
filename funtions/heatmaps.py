import pandas as pd
import plotly.express as px
import streamlit as st

from funtions import general


def get_dfHeatmaps(df: pd.DataFrame, year: int) -> pd.DataFrame:

    df_heatmap: pd.DataFrame = df[df["dates (Y-M-D hh:mm:ss)"].dt.year == year]
    df_heatmap["dateOfYear"] = df_heatmap["dates (Y-M-D hh:mm:ss)"].dt.date
    df_heatmap["hourOfDay"] = df_heatmap["dates (Y-M-D hh:mm:ss)"].dt.hour

    return df_heatmap

def get_dfPivot(df: pd.DataFrame, Label: str, year: int) -> pd.DataFrame:

    df_heatmap = get_dfHeatmaps(df, year)

    pivot = df_heatmap.pivot_table(
        index="hourOfDay",
        columns="dateOfYear",
        values=Label,
        aggfunc="mean"
    )

    return pivot

def get_heatmaps(df: pd.DataFrame, timeInfoYears: list, Label: str, Name: str, config_PX: dict):

    for year in timeInfoYears:
        df_pivot = get_dfPivot(df, Label, year)

        fig = px.imshow(
            df_pivot,
            aspect="auto",
            color_continuous_scale="Turbo",
            origin="lower",
            labels={
                "x": "Fecha",
                "y": "Hora",
                "color": Name
            }
        )

        fig.update_xaxes(
            tickformat="%d-%m-%Y",
            tickangle=45
        )

        fig.update_layout(
            title=f"Heatmap de {Name} para el año {year}",
            xaxis_nticks=12
        )

        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True, config=config_PX)

            dictDownload = {
                "Xlsx": {
                    "label": f"Datos heatmap de {Name} para el {year}",
                    "type_file": "xlsx",
                    "fileName": f"PES_heatmap{Label[:Label.find('(')-1]}{year}",
                    "nime": "xlsx",
                    "emoji": "📄",
                    "key": f"PES_heatmap{Label[:Label.find('(')-1]}{year}",
                    "type": "secondary"
                }
            }

            general.getDownloadButtons(dictDownload=dictDownload, df=df_pivot, dictionary=None)

    return

# heatmap
        # if "ALLSKY_SFC_SW_DWN" in listColumnsKeys:
        #     for year in timeInfo["years"]:
        #         df_heatmap: pd.DataFrame = df[df["dates (Y-M-D hh:mm:ss)"].dt.year == year]
        #         df_heatmap["dateOfYear"] = df_heatmap["dates (Y-M-D hh:mm:ss)"].dt.date
        #         df_heatmap["dayOfYear"] = df_heatmap["dates (Y-M-D hh:mm:ss)"].dt.dayofyear
        #         df_heatmap["hourOfDay"] = df_heatmap["dates (Y-M-D hh:mm:ss)"].dt.hour

        #         pivot = df_heatmap.pivot_table(
        #             index="hourOfDay",
        #             columns="dateOfYear",
        #             values=DICT_PARAMS["ALLSKY_SFC_SW_DWN"]["Label"],
        #             aggfunc="mean"
        #         )

        #         st.dataframe(pivot)

        #         fig = px.imshow(
        #             pivot,
        #             aspect="auto",
        #             color_continuous_scale="Turbo",
        #             origin="lower",
        #             labels={
        #                 "x": "Fecha",
        #                 "y": "Hora",
        #                 "color": DICT_PARAMS["ALLSKY_SFC_SW_DWN"]["Name"]
        #             }
        #         )

        #         fig.update_xaxes(
        #             tickformat="%d-%m-%Y",       # Formato de fecha
        #             tickangle=0
        #             )

        #         fig.update_layout(
        #             title="Heatmap de Irradiancia Solar (W/m²)",
        #             xaxis_nticks=12    # menos saturado
        #         )

        #         with st.container(border=True):
        #             st.plotly_chart(fig, use_container_width=True, config=CONFIG_PX)