# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import streamlit as st
import datetime
import plotly.graph_objects as go
import plotly.express as px
from pvlib.location import Location

from data.param import DICT_PARAMS

azimuth = DICT_PARAMS["SUN_AZMT"]["Label"]
elevation = DICT_PARAMS["SUN_ELVT"]["Label"]

dict_download = {
    "Xlsx": {
        "label": "Carta solar",
        "type_file": "xlsx",
        "fileName": "PES_addSolarChart",
        "nime": "xlsx",
        "emoji": ":material/file_save:",
        "key": "PES_addSolarChart",
        "type": "secondary"
    }
}

def get_color(val, vmin, vmax):

    norm = (val - vmin) / (vmax - vmin)
    return px.colors.sample_colorscale('Inferno', norm)[0]

def get_df_solar(df:pd.DataFrame, latitude, longitude, tz) -> pd.DataFrame:

    df_solar = df.copy()
    df_solar["dates (Y-M-D hh:mm:ss)"] = pd.to_datetime(df_solar["dates (Y-M-D hh:mm:ss)"])
    df_solar = df_solar.set_index("dates (Y-M-D hh:mm:ss)")
    df_solar.index = df_solar.index.tz_localize(tz)

    site = Location(latitude=latitude, longitude=longitude, tz=tz)
    solarPos = site.get_solarposition(df_solar.index)

    df_solar[azimuth] = solarPos["azimuth"]
    df_solar[elevation] = solarPos["apparent_elevation"]

    df_solar.loc[df_solar[elevation] < 0, [azimuth, elevation]] = np.nan

    df_solar = df_solar.reset_index()
    df_solar["dates (Y-M-D hh:mm:ss)"] = df_solar["dates (Y-M-D hh:mm:ss)"].dt.tz_localize(None)

    return df_solar

def plotlySolarProjection(df: pd.DataFrame):

    df["month"] = df["dates (Y-M-D hh:mm:ss)"].dt.month
    df["hour"] = df["dates (Y-M-D hh:mm:ss)"].dt.hour
    df["minute"] = df["dates (Y-M-D hh:mm:ss)"].dt.minute

    fig = go.Figure()

    colores = px.colors.sequential.Turbo
    name_months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

    for m in range(1, 13):
        df_month = df[df['month'] == m]
        if df_month.empty: continue
        
        hover_text = [
            f"Fecha: {dt.strftime('%d/%m/%Y')}<br>Hora: {dt.strftime('%H:%M')}<br>Azimut: {az:.1f}°<br>Elevación: {el:.1f}°" 
            if pd.notna(el) else "" 
            for dt, az, el in zip(df_month["dates (Y-M-D hh:mm:ss)"], df_month[azimuth], df_month[elevation])
        ]

        fig.add_trace(go.Scatterpolar(
            r=df_month[elevation], 
            theta=df_month[azimuth],
            mode='lines',
            name=name_months[m-1],
            line=dict(color=colores[m-1], width=1.5),
            text=hover_text,
            hoverinfo="text",
            connectgaps=False
        ))

    horas_diurnas = sorted(df[df[elevation].notna()]['hour'].unique())

    for h in horas_diurnas:
        df_hour = df[(df['hour'] == h) & (df['minute'] == 0)].dropna(subset=[elevation])
        
        if len(df_hour) > 1:
            idx_max = df_hour[elevation].argmax()
            text_labels = [f"{int(h)}:00" if i == idx_max else "" for i in range(len(df_hour))]
            
            fig.add_trace(go.Scatterpolar(
                r=df_hour[elevation],
                theta=df_hour[azimuth],
                mode='lines+text',
                name=f"{int(h)}:00",
                line=dict(color='gray', dash='dot', width=1.2),
                text=text_labels,
                textposition="top center",
                textfont=dict(size=10, color="black"),
                hoverinfo='skip',
                showlegend=False
            ))

    fig.update_layout(
        polar=dict(
            bgcolor="white",
            radialaxis=dict(
                range=[90, 0],
                tickvals=[0, 15, 30, 45, 60, 75, 90],
                ticktext=['0°', '15°', '30°', '45°', '60°', '75°', '90°'],
                gridcolor='lightgray',
                angle=45,
                tickfont=dict(size=9, color="gray")
            ),
            angularaxis=dict(
                rotation=90,
                direction='clockwise',
                tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                ticktext=['N (0°)', 'NE', 'E (90°)', 'SE', 'S (180°)', 'SO', 'O (270°)', 'NO'],
                gridcolor='lightgray'
            )
        ),
        height=600,
        margin=dict(t=50, b=50, l=50, r=50),
        legend=dict(title="Meses", orientation="v", y=0.5, x=1.15)
    )

    st.plotly_chart(fig, use_container_width=True)

    df = df.drop(columns=["month", "hour", "minute"])

    return

def plotyCylindricalProjection(df: pd.DataFrame):

    fig = go.Figure()

    colors = px.colors.sequential.Turbo
    name_months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

    for m in range(1, 13):
        df_month = df[df['month'] == m]
        if df_month.empty: continue
        
        hover_text = [
            f"Fecha: {dt.strftime('%d/%m/%Y')}<br>Hora: {dt.strftime('%H:%M')}<br>Azimut: {az:.1f}°<br>Elevación: {el:.1f}°" 
            if pd.notna(el) else "" 
            for dt, az, el in zip(df_month["dates (Y-M-D hh:mm:ss)"], df_month[azimuth], df_month[elevation])
        ]

        fig.add_trace(go.Scatter(
            x=df_month[azimuth],
            y=df_month[elevation],
            mode='lines',
            name=name_months[m-1],
            line=dict(color=colors[m-1], width=0.8),
            text=hover_text,
            hoverinfo="text",
            connectgaps=False
        ))

    horas_validas = sorted(df['hour'].dropna().unique())
    for h in horas_validas:
        if 6 <= h <= 18:
            df_hour = df[(df['hour'] == h) & (df['minute'] == 0)].dropna()
            
            if not df_hour.empty:
                idx_max = df_hour[elevation].argmax() if len(df_hour) > 0 else 0
                text_labels = [f"{int(h)}:00" if i == idx_max else "" for i in range(len(df_hour))]
                
                fig.add_trace(go.Scatter(
                    x=df_hour[azimuth],
                    y=df_hour[elevation],
                    mode='lines+text',
                    name=f"{int(h)}:00",
                    line=dict(color='gray', dash='dot', width=1.2),
                    text=text_labels,
                    textposition="top center",
                    textfont=dict(size=10, color="black"),
                    hoverinfo='skip',
                    showlegend=False
                ))

    fig.update_layout(
        xaxis=dict(
            title="Azimut Solar (°)",
            range=[60, 300], 
            tickvals=[60, 90, 120, 150, 180, 210, 240, 270, 300],
            ticktext=['60°', 'Este (90°)', '120°', '150°', 'Sur (180°)', '210°', '240°', 'Oeste (270°)', '300°'],
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False
        ),
        yaxis=dict(
            title="Elevación Solar (°)",
            range=[0, 90],
            tickvals=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90],
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='black'
        ),
        plot_bgcolor="white",
        height=600,
        margin=dict(t=50, b=50, l=50, r=50),
        legend=dict(title="Meses", orientation="v", y=0.5, x=1.05)
    )

    st.plotly_chart(fig, use_container_width=True)

    return

def viewDataframeSolarChart(df: pd.DataFrame):
     
    sub_tab1, sub_tab2 = st.tabs([":material/explore: Proyección Estereográfica", "Proyección Cilíndrica"])

    with sub_tab1:
        plotlySolarProjection(df)
    with sub_tab2:
        plotyCylindricalProjection(df)
     
    return



            