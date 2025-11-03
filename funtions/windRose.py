import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

DIRECTION_NAMES = ("N","NNE","NE","ENE"
                   ,"E","ESE","SE","SSE"
                   ,"S","SSW","SW","WSW"
                   ,"W","WNW","NW","NNW")

DIRECTION_ANGLES = np.arange(0, 2*np.pi, 2*np.pi/16)

def windrose_histogram(wspd, wdir, speed_bins=12, normed=False, norm_axis=None):
    
    if isinstance(speed_bins, int):
        speed_bins = np.linspace(0, wspd.max(), speed_bins)

    num_spd = len(speed_bins)
    num_angle = 16

    wdir_shifted = (wdir + 11.25) % 360

    angle_bins = np.linspace(0, 360, num_angle + 1)

    hist, *_ = np.histogram2d(wspd, wdir_shifted, bins=(speed_bins, angle_bins))

    if normed:
        hist /= hist.sum(axis=norm_axis, keepdims=True)
        hist *= 100

    return hist, angle_bins, speed_bins

def make_wind_df(data_df: pd.DataFrame, ws_label: str, wd_label: str, normed=True, norm_axis=None) -> pd.DataFrame:

    max_speed = int(np.ceil(data_df[ws_label].max()))
    num_partitions = max_speed
        
    wspd = data_df[ws_label].values
    wdir = data_df[wd_label].values

    if max_speed is None:
        speed_bins = np.linspace(0, wspd.max(), num_partitions + 1)
    else:
        speed_bins = np.append(np.linspace(0, max_speed, num_partitions + 1), np.inf)

    h, *_ = windrose_histogram(wspd, wdir, speed_bins, normed=normed, norm_axis=norm_axis)
 
    wind_df = pd.DataFrame(data=h, columns=DIRECTION_NAMES)

    speed_bin_names = []
    speed_bins_rounded = [round(i, 2) for i in speed_bins]
    for start, end in zip(speed_bins_rounded[:-1], speed_bins_rounded[1:]):
        speed_bin_names.append(f'{start:g}-{end:g}' if end < np.inf else f'>{start:g}')

    wind_df['strength'] = speed_bin_names

    wind_df = wind_df.melt(id_vars=['strength'], var_name='direction', value_name='frequency')

    return wind_df

def get_colors_of_strength(wind_df: pd.DataFrame) -> dict:

    strengths = sorted(wind_df["strength"].unique(), key=lambda x:float(x.split('-')[0] if '-' in x else x[1:]))
    colours = px.colors.sample_colorscale(px.colors.get_colorscale('Magma_r'), len(strengths))
    colour_dict = dict(zip(strengths, colours))

    return colour_dict

def plotly_windrose(wind_df: pd.DataFrame, color_discrete_map: dict, config: dict, column_name: str):
    
    wind_df['frequency'] = wind_df['frequency'] / 100

    fig = px.bar_polar(wind_df, r="frequency", theta="direction", 
                       color="strength",
                       color_discrete_map=color_discrete_map,
                       labels={
                           "strength": "Rango (m/s)",
                           "frequency": "Frecuencia",
                           "direction": "Dirección"
                       },
                       title=f"Rosa de los Vientos ({column_name})"
                   )
    
    fig.update_polars(
        radialaxis_angle = -45,
        radialaxis_tickangle=-45,
        radialaxis_tickformat=',.0%',
        radialaxis_tickfont_color='black',
    )
    
    fig.update_layout(
        autosize=True,
    )

    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, config=config)

    return

def plotly_windhist(wind_df: pd.DataFrame, color_discrete_map: dict, config: dict, column_name: str):

    wind_df["frequency"] = wind_df["frequency"]*100

    df_totales: pd.DataFrame = wind_df.groupby("direction", as_index=False)["frequency"].sum()
    df_totales.rename(columns={'frequency': 'total_frequency'}, inplace=True)

    fig = px.bar(
        wind_df,
        x="direction",
        y="frequency",
        color="strength",
        color_discrete_map=color_discrete_map,
        title=f"Frecuencia por Dirección y Rango ({column_name})",
        labels={
            "direction": "Dirección",
            "frequency": "Frecuencia(%)",
            "strength": "Rango"
        }
    )

    annotations = []
    for index, row in df_totales.iterrows():
        annotations.append(dict(
            x=row["direction"],
            y=row["total_frequency"],
            text=f"{round(row['total_frequency'], 2)}",
            showarrow=False,
            yshift=10,
            font=dict(size=10, color="black")
        ))

    fig.update_layout(
        barmode="stack",
        annotations=annotations
    )

    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, config=config)

    return