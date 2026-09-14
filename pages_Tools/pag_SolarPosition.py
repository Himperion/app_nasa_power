# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime as dt
import calendar, folium, yaml
from streamlit_folium import st_folium
from funtions import fun_ClimateData, geoData, solarCard, viewData


#%% session_state

if "df_data" not in st.session_state:
    st.session_state["df_data"] = None
if "flagCalRows" not in st.session_state:
    st.session_state["flagCalRows"] = False

#%% global variables

dict_download = solarCard.dict_download

optSelTimePrints = [
    ":material/edit_calendar: Selección de fecha y hora",
    ":material/upload_file: Cargar archivo con estampa de tiempo"
]

latitude, longitude = None, None
uploadedXlsxDATES = None

#%% main

st.header(":material/wb_sunny: **Carta solar**")

with st.container(border=True):

    st.markdown("**:material/globe_location_pin: Ingreso de datos geográficos**")

    dataEntryOptions = st.selectbox(label="Opciones de ingreso de datos", options=fun_ClimateData.selectDataEntryOptions,
                                    index=0, placeholder="Selecciona una opción")
        
    if dataEntryOptions == fun_ClimateData.selectDataEntryOptions[0]:
        flag_submittedTab1 = False
        click_map = folium.Map(location=[7.142056, -73.121231], zoom_start=18)
        click_marker = folium.LatLngPopup()
        click_map.add_child(click_marker)

        with st.container(height=400):
            map_local = st_folium(click_map, height=367, use_container_width=True)

        if map_local and map_local["last_clicked"]:
            coords = map_local["last_clicked"]
            latitude, longitude = round(coords['lat'], 5), round(coords['lng'], 5)

            with st.container(border=False):
                country, flag = geoData.getCountryAndFlag(lat=latitude, lon=longitude)

                col1, col2, col3, col4 = st.columns([0.25, 0.25, 0.25, 0.25])
                col1.markdown(f"**:blue[{country}:]** {flag}")
                col2.markdown(f"**:blue[Latitud:]** {latitude}")
                col3.markdown(f"**:blue[Longitud:]** {longitude}")

    elif dataEntryOptions == fun_ClimateData.selectDataEntryOptions[1]:
        flag_submittedTab1 = False
        coordinate_options = st.selectbox(label="Opciones de ingreso de coordenadas geográficas",
                                            options=fun_ClimateData.selectCoordinateOptions,
                                            index=1, placeholder="Selecciona una opción")
        
        if coordinate_options == fun_ClimateData.selectCoordinateOptions[0]:
            latitude, longitude = fun_ClimateData.get_GMS_2_GD()
        elif coordinate_options == fun_ClimateData.selectCoordinateOptions[1]:
            latitude, longitude = fun_ClimateData.get_number_input_latitude_longitude(lat_value=7.142056, lon_value=-73.12123)

    elif dataEntryOptions == fun_ClimateData.selectDataEntryOptions[2]:
        flag_submittedTab1 = False
        with st.container(border=True):
            uploadedFileYaml = st.file_uploader(label="Sube tu archivo YAML", type=["yaml", "yml"])

with st.container(border=True):

    st.markdown("**:material/date_range: Ingreso de estampas de tiempo**")

    optionsTimePrints = st.radio(
        label="Opciones para el ingreso de rango de tiempo",
        options=optSelTimePrints,
        captions=["Ingreso manual de datos horarios", "Carga de archivo EXCEL (.xlsx) con columna de estampas de tiempo"],
        index=0
    )

    if optionsTimePrints == optSelTimePrints[0]:

        dateNow = dt.datetime.now()

        selTimeDelta = st.select_slider(
            label=":material/timer: Seleccionar delta en minutos de las muestras para el rango horario",
            options=list(range(5,65,5)),
            value=15
        )

        col1, col2 = st.columns(2)

        with col1:
            startDate = st.datetime_input(
                label=":material/today: Fecha de inicio:",
                value=dt.datetime(dateNow.year, dateNow.month, 1, 0, 0),
                step=dt.timedelta(minutes=selTimeDelta)
            )

        with col2:
            endDate = st.datetime_input(
                label=":material/event: Fecha final:",
                value=dt.datetime(dateNow.year, dateNow.month, calendar.monthrange(dateNow.year, dateNow.month)[1], 23, 45),
                step=dt.timedelta(minutes=selTimeDelta)
            )

        if startDate is not None and endDate is not None:
            calRows = fun_ClimateData.cal_rows(startDate, endDate, steps=selTimeDelta)

            if calRows < 0:
                st.session_state["flagCalRows"] = False
                st.error("La **Fecha final** debe ser mayor a la **Fecha de inicio**", icon=":material/error:")
            else:
                st.session_state["flagCalRows"] = True



    elif optionsTimePrints == optSelTimePrints[1]:

        uploadedXlsxDATES = st.file_uploader(label=f":material/upload_file: Cargar archivo de **estampas de tiempo**", type=["xlsx"], key="uploadedXlsxDATES")

    # if uploadedXlsxDATES is not None:
    #     df_dates = pd.read_excel(uploadedXlsxDATES)
    #     df_dates["dates (Y-M-D hh:mm:ss)"] = pd.to_datetime(df_dates["dates (Y-M-D hh:mm:ss)"])
    #     df_dates = df_dates.set_index("dates (Y-M-D hh:mm:ss)")

submitted = st.button("Aceptar")

if submitted:
    if latitude is not None and longitude is not None:
        if optionsTimePrints == optSelTimePrints[0]:
            if st.session_state["flagCalRows"]:
                timeRange = pd.date_range(start=startDate, end=endDate, freq=dt.timedelta(minutes=selTimeDelta))

                df_data = pd.DataFrame({"dates (Y-M-D hh:mm:ss)": timeRange})
                df_data = solarCard.get_df_solar(df_data, latitude, longitude, "America/Bogota")

                st.session_state["df_data"] = df_data

                del df_data
            else:
                st.error("La **Fecha final** debe ser mayor a la **Fecha de inicio**", icon=":material/error:")
        elif optionsTimePrints == optSelTimePrints[1]:
            if uploadedXlsxDATES is not None:
                try:
                    df_data = pd.read_excel(uploadedXlsxDATES)
                    df_data = solarCard.get_df_solar(df_data, latitude, longitude, "America/Bogota")

                    st.session_state["df_data"] = df_data

                    del df_data

                except:
                    st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon=":material/error:")
            else:
                st.warning("Cargar archivo **EXCEL** (.xlsx)", icon=":material/error:")
    else:
        st.warning("Ingresar coordenadas geográficas", icon=":material/warning")

if st.session_state["df_data"] is not None:
    viewData.viewInformation(st.session_state["df_data"], None, dict_download)



# if submitted:
#     if uploadedXlsxDATES is not None:
#         if latitude is not None and longitude is not None:
#             try:
#                 df_data = pd.read_excel(uploadedXlsxDATES)
#                 df_data = solarCard.get_df_solar(df_data, latitude, longitude, "America/Bogota")

#                 st.session_state["dict_params"] = {
#                     "df_data": df_data,
#                 }

#             except:
#                 st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon=":material/error:")
#         else:
#             st.warning("Ingresar coordenadas geográficas", icon=":material/warning")
#     else:
#         st.error("Cargar archivo **EXCEL** (.xlsx)", icon=":material/error:")

# if st.session_state["dict_params"] is not None:
#     # st.dataframe(st.session_state["dict_params"]["df_data"])

#     general.viewInformation(st.session_state["dict_params"]["df_data"], None, dict_download)


# if accept:
#     if latitude is not None and longitude is not None:
#         if df_dates is not None:
#             st.session_state["dataSolar"] = {
#                 "latitude": latitude,
#                 "longitude": longitude,
#                 "df_solar": solarCard.get_df_solar(df_dates, latitude, longitude, "America/Bogota")
#             }
            
#         else:
#             st.warning("Cargue un archivo de fechas (.xlsx) para continuar.", icon=":material/warning_off:")
#     else:
#         st.warning("Seleccione una ubicación en el mapa o ingrese coordenadas para continuar.", icon=":material/warning_off:")

# if  st.session_state["dataSolar"] is not None:

#     df_solar: pd.DataFrame = st.session_state["dataSolar"]["df_solar"]

#     # st.dataframe(df_solar)

#     min_value = df_solar.index.min().date()
#     max_value = df_solar.index.max().date()

#     with st.form('form'):
#         st.markdown(":material/edit_calendar: **:blue[{0}:]**".format("Estampa de tiempo"))

#         col1, col2 = st.columns(2)
#         with col1:
#             date_ini = st.date_input("Fecha de Inicio:", min_value=min_value, max_value=max_value, value=min_value, key="date_ini_tab1")
#         with col2:
#             date_end = st.date_input("Fecha Final:", min_value=min_value, max_value=max_value, value=max_value, key="date_end_tab1")

#         accept_form = st.form_submit_button("Aceptar")

#     if accept_form:
#         cal_rows = fun_ClimateData.cal_rows(date_ini, date_end, steps=60)

#         if cal_rows >= 0:
#             mask = (df_solar.index.date >= date_ini) & (df_solar.index.date <= date_end)
#             df_filter = df_solar[mask].copy()

#             sub_tab1, sub_tab2 = st.tabs([":material/explore: Proyección Estereográfica", "Proyección Cilíndrica"])

#             with sub_tab1:
#                 solarCard.plotlySolarProjection(df=df_filter)
#             with sub_tab2:
#                 solarCard.plotyCylindricalProjection(df=df_filter)
#         else:
#             st.warning("La {0} debe ser menor a la {1}".format(":blue[Fecha de Inicio]", ":blue[Fecha final]"), icon=":material/warning_off:")


# # 1. La Bóveda Celeste en 3D (Sky Dome)