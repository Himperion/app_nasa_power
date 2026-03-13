# -*- coding: utf-8 -*-
import streamlit as st
import folium, yaml
from streamlit_folium import st_folium
from funtions import fun_ClimateData, general, geoData

#%% cache_data

@st.cache_data
def get_outForm1(dict_params, dict_parameters, options, cal_rows):

    data = fun_ClimateData.get_out(dict_params, dict_parameters, options, cal_rows)

    return data


#%% global variables

min_value, max_value = general.get_date_imput_nasa()

with open(general.resource_path("files//dict_parameters.yaml"), 'r') as archivo:
    dict_parameters = yaml.safe_load(archivo)

dict_downloadTap1 = fun_ClimateData.dict_download

latitude, longitude = None, None
flag_submittedTab1 = False

#%% session_state

if "dict_paramsForm1" not in st.session_state:
    st.session_state["dict_paramsForm1"] = None

#%% main

st.header(":material/partly_cloudy_day: **Datos climáticos y potencial energético**")

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
    
    with st.container(border=True):
        st.markdown(":material/globe_location_pin: **:blue[{0}:]**".format("Datos del sitio"))
        if coordinate_options == fun_ClimateData.selectCoordinateOptions[0]:
            latitude, longitude = fun_ClimateData.get_GMS_2_GD()
        elif coordinate_options == fun_ClimateData.selectCoordinateOptions[1]:
            latitude, longitude = fun_ClimateData.get_number_input_latitude_longitude(lat_value=7.142056, lon_value=-73.12123)

elif dataEntryOptions == fun_ClimateData.selectDataEntryOptions[2]:
    flag_submittedTab1 = False
    with st.container(border=True):
        uploadedFileYaml = st.file_uploader(label="Sube tu archivo YAML", type=["yaml", "yml"])

with st.form('form1'):
    if dataEntryOptions == fun_ClimateData.selectDataEntryOptions[0] or dataEntryOptions == fun_ClimateData.selectDataEntryOptions[1]:
        with st.container(border=True):
            st.markdown(":material/edit_calendar: **:blue[{0}:]**".format("Estampa de tiempo"))
            col1, col2 = st.columns(2)
            date_ini = col1.date_input("Fecha de Inicio:", max_value=min_value)
            date_end = col2.date_input("Fecha Final:", max_value=max_value)

    parameterOptions = fun_ClimateData.get_parameterOptions(dict_parameters)
    options = fun_ClimateData.get_multiselect_params(list_show_output=parameterOptions)

    submittedTab1 = st.form_submit_button("Aceptar")

    if submittedTab1:
        if dataEntryOptions == fun_ClimateData.selectDataEntryOptions[0] or dataEntryOptions == fun_ClimateData.selectDataEntryOptions[1]:
            if latitude is not None and longitude is not None:
                st.session_state['dict_paramsForm1'] = {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                    "start": date_ini,
                    "end": date_end
                    }
                flag_submittedTab1 = True
            else:
                st.warning("Ingrese una latitud y longitud en el mapa interactivo", icon=":material/warning_off:")
 
        elif dataEntryOptions == fun_ClimateData.selectDataEntryOptions[2]:
            if uploadedFileYaml is not None:
                try:
                    st.session_state['dict_paramsForm1'] = yaml.safe_load(uploadedFileYaml)
                    flag_submittedTab1 = True
                except:
                    st.error("Error al cargar archivo **YAML** (.yaml)", icon=":material/error:")
            else:
                st.warning("Cargar archivo **YAML** (.yaml)", icon=":material/warning_off:")

if st.session_state["dict_paramsForm1"] is not None and flag_submittedTab1:   
    dict_params = st.session_state["dict_paramsForm1"]
    cal_rows = fun_ClimateData.cal_rows(dict_params["start"], dict_params["end"], steps=60)

    if len(options) != 0:
        if cal_rows > 0:
            dict_outForm1 = {
                "dict_params" : dict_params,
                "dict_parameters": dict_parameters,
                "options": options,
                "cal_rows": cal_rows
            }
            data = get_outForm1(**dict_outForm1)
            general.viewInformation(data, dict_params, dict_downloadTap1)
    
        else:
            if cal_rows == 0:
                st.warning("La {0} debe ser diferente a la {1}".format(":blue[Fecha de Inicio]", ":blue[Fecha final]"), icon=":material/warning_off:")
            if cal_rows < 0:
                st.warning("La {0} debe ser menor a la {1}".format(":blue[Fecha de Inicio]", ":blue[Fecha final]"), icon=":material/warning_off:")
    else:
        st.warning("Ingrese por lo menos una opción en {0}".format(":blue[Seleccione los datos a cargar]"), icon=":material/warning_off:")