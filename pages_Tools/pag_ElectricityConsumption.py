# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from funtions import general
from funtions import fun_ElectricityConsumption, general

#%% cache_data

@st.cache_data
def get_outForm3(df_data, df_loadResized, columnLoad, range_variation):

    data = fun_ElectricityConsumption.addLoadData(df_data, df_loadResized, columnLoad, range_variation)

    return data

#%% session_state

if "dict_paramsForm3" not in st.session_state:
    st.session_state["dict_paramsForm3"] = None

#%% global variables

dict_downloadTap3 = fun_ElectricityConsumption.dict_download

labelUploadedYamlDATA = 'Datos climáticos y potencial energético del sitio'
opt_load_profile = ["ESSA", "Personalizado"]

df_loadPU = pd.read_excel(general.resource_path("files/[Plantilla] - CargaPU ESSA.xlsx"))
columns_load = df_loadPU.columns.to_list()[1:]
default_kWh_day = 1.126
df_loadResized = None

#%% main

st.header(":material/electrical_services: Consumo eléctrico")

with st.container(border=True):
    typeLoad = st.selectbox(label="Perfil de carga", options=opt_load_profile, index=0)

    if typeLoad == opt_load_profile[0]:
        col1, col2 = st.columns(2)
        with col1:
            typeLoad = st.selectbox(label="Tipo de carga", options=columns_load, index=0)
        with col2:
            kWh_day = st.number_input(label="Consumo (kWh/día)", min_value=0.0, max_value=100.0, format="%0.2f",
                                        step=0.01, value=default_kWh_day)
        if typeLoad is not None:
            df_loadResized = general.get_df_load_resized(df_loadPU, kWh_day, typeLoad)
            general.graphDataframe(df_loadResized, "Hora", f"{typeLoad} (kW)", "teal", "Potencia (kW)", "Curva De Demanda")

    elif typeLoad == opt_load_profile[1]:
        columnLoad = f"{typeLoad} (kW)"
        with st.container(border=True):
            
            st.markdown(":material/insert_chart: **:blue[{0}:]**".format("Perfil de carga"))

            col1, col2 = st.columns(2, vertical_alignment="bottom")
            
            radioLoad = col1.radio(label="Opciones para el ingreso de perfil de carga",
                                    options=["W", "kW", "P.U."],
                                    captions=["Ingreso de muestras en Watts (W)", "Ingreso de muestras en kilovatios (kW)", "Ingreso demuestras en sistema POR-UNIDAD"])
            
            if radioLoad == "P.U.":
                kWh_day = col2.number_input(label="Consumo (kWh/día)", min_value=0.0, max_value=100.0, format="%0.2f",
                                            step=0.01, value=default_kWh_day)
            else:
                kWh_day = None

            uploadedXlsxLOAD = st.file_uploader(label=f":material/upload_file: Cargar archivo **perfil de carga eléctrica**", type=["xlsx"], key="uploadedXlsxLOAD")

            if uploadedXlsxLOAD is not None:
                df_loadResized = fun_ElectricityConsumption.get_dfLoadProfile(uploadedXlsx=uploadedXlsxLOAD, optionLoad=radioLoad, kWh_day=kWh_day, columnLoad=columnLoad)
            if df_loadResized is not None:
                general.graphDataframe(df_loadResized, "Hora", f"{typeLoad} (kW)", "teal", "Potencia (kW)", "Curva De Demanda")


            with open("files/[Plantilla] - AddLoad.xlsx", "rb") as file:
                st.download_button(label="Descargar plantilla **:blue[Perfil de carga eléctrica]**:", data=file, icon="📄",
                                    file_name="IngresoPerfilDeCarga.xlsx", mime="xlsx")


        
        
        # df_loadResized = pd.DataFrame(load_time_stamp, columns=[columnLoad])
        # df_loadResized["Hora"] = list(range(0,24,1))

        # if df_loadResized is not None:
        #     with st.container(border=True):
        #         general.graphDataframe(df_loadResized, "Hora", columnLoad, "teal", "Potencia (kW)", False)

    with st.container(border=True):
        uploadedXlsxDATA = st.file_uploader(label=f":material/upload_file: **Cargar archivo {labelUploadedYamlDATA}**", type=["xlsx"], key="uploadedXlsxDATA")
        range_variation = st.select_slider(label="Rango de variación de las muestras", options=[f"{-30+i}%" for i in range(0,61,1)], value=("-10%", "10%"))
        
    submittedTab3 = st.button("Aceptar")

    if submittedTab3:
        if uploadedXlsxDATA is not None:
            try:
                df_data = pd.read_excel(uploadedXlsxDATA)
                checkTime, timeInfo = fun_ElectricityConsumption.checkTimeData(df_data, deltaMinutes=60)

                if checkTime and df_loadResized is not None:
                    df_data = fun_ElectricityConsumption.addLoadData(df_data, df_loadResized, f"{typeLoad} (kW)", range_variation)

                    st.session_state['dict_paramsForm3'] = {
                        "df_data": df_data,
                        "df_loadResized": df_loadResized,
                        "columnLoad": f"{typeLoad} (kW)",
                        "range_variation": range_variation
                        }

            except:
                st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon=":material/error:")
        else:
            st.error(f"Cargar archivo **{labelUploadedYamlDATA}**", icon=":material/error:")

if st.session_state["dict_paramsForm3"] is not None:
    data = get_outForm3(**st.session_state["dict_paramsForm3"])
    general.viewInformation(data, None, dict_downloadTap3)

