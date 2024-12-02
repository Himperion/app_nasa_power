import streamlit as st
import pandas as pd
import folium, warnings, io, yaml
from streamlit_folium import st_folium

from funtions import funTap1, funTap2, funTap3

warnings.filterwarnings("ignore")

#%% global variables

dict_parameters = {
    "Irradiancia (W/m^2)": ("ALLSKY_SFC_SW_DWN", "Gin(W/m²)"),
    "Velocidad del viento a 10 msnm (m/s)": ("WS10M", "Vwind 10msnm(m/s)"),
    "Velocidad del viento a 50 msnm (m/s)": ("WS50M", "Vwind 50msnm(m/s)"),
    "Temperatura ambiente a 2 msnm (°C)": ("T2M", "Tamb 2msnm(°C)")
}

template = {
    "directory": "files",
    "name_file": "[Plantilla] - Temperatura de operación",
    "format_file": "xlsx",
    "description": "Irradiancia efectiva y Temperatura ambiente del sitio"
}

constants_GD = {
    "alpha": 0.1,
    "tol": 0.001,
    "iter_max": 1000
}

NOCT = {
    "description": "Temperatura de operaci\xF3n nominal de la celda",
    "label": "NOCT",
    "number_input": {
        "format": None,
        "max_value": 90,
        "min_value": 1,
        "step": None,
        "value": 42
    },
    "unit": "°C",
    "data_type": float
}

if 'dict_params' not in st.session_state:
    st.session_state['dict_params'] = None

options_multiselect = list(dict_parameters.keys())

list_tabs = [
    "🌤️ Datos climáticos y potencial energético",
    "🌡️ Temperatura de operación",
    "⏱️ Aumentar número de muestras"
    ]

selectDataEntryOptions = [
    "🌎 Mapa interactivo",
    "📌 Datos del sitio",
    "💾 Cargar archivo de datos del sitio YAML"
    ]

selectCoordinateOptions = [
    "Sistema sexagesimal GMS",
    "Sistema decimal GD"
    ]

latitude, longitude, data_dates = None, None, None

def tab1():
    latitude, longitude = None, None
    
    st.header(list_tabs[0])

    dataEntryOptions = st.selectbox(label="Opciones de ingreso de datos", options=selectDataEntryOptions,
                                      index=0, placeholder="Selecciona una opción")
    
    if dataEntryOptions == selectDataEntryOptions[0]:
        click_map = folium.Map(location=[7.142056, -73.121231], zoom_start=18)
        click_marker = folium.LatLngPopup()
        click_map.add_child(click_marker)

        with st.container(height=400):
            map_local = st_folium(click_map, width=700, height=400)

        if map_local and map_local["last_clicked"]:
            coords = map_local["last_clicked"]
            latitude = round(coords['lat'], 5)
            longitude = round(coords['lng'], 5)

            st.markdown(f"**:blue[Latitud:]** {latitude} **:blue[Longitud:]** {longitude}")

    elif dataEntryOptions == selectDataEntryOptions[1]:
        coordinate_options = st.selectbox(label="Opciones de ingreso de coordenadas geográficas",
                                          options=selectCoordinateOptions,
                                          index=1, placeholder="Selecciona una opción")
        
        with st.container(border=True):
            st.markdown("🌎 **:blue[{0}:]**".format("Datos del sitio"))
        
            if coordinate_options == selectCoordinateOptions[0]:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns(4)

                    NS = col1.selectbox("**Latitud:**", ["N", "S"], index=0)
                    lat_degrees = col2.number_input(label="Grados", min_value=0, value=7)
                    lat_minutes = col3.number_input(label="Minutos", min_value=0, value=8)
                    lat_seconds = col4.number_input(label="Segundos", min_value=0.0, format="%.4f", value=31.4016)

                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns(4)

                    EO = col1.selectbox("**Longitud:**", ["W", "E"], index=0)
                    lon_degrees = col2.number_input(label="Grados", min_value=0, value=73)
                    lon_minutes = col3.number_input(label="Minutos", min_value=0, value=7)
                    lon_seconds = col4.number_input(label="Segundos", min_value=0.0, format="%.4f", value=16.4316)

            elif coordinate_options == selectCoordinateOptions[1]:
                col1, col2 = st.columns(2)

                lat_input = col1.number_input('Ingrese la latitud:', min_value=-90.0, max_value=90.0, step=0.000001, format="%.6f", value=7.142056)
                lon_input = col2.number_input('Ingrese la longitud:', min_value=-180.0, max_value=180.0, step=0.000001, format="%.6f", value=-73.121231)

            else:
                with st.container(border=True):
                    uploadedFileYaml = st.file_uploader(label="Sube tu archivo YAML", type=["yaml", "yml"])

    with st.form('form1'):
        if dataEntryOptions == selectDataEntryOptions[0] or dataEntryOptions == selectDataEntryOptions[1]:
            
            with st.container(border=True):
                st.markdown("🗓️ **:blue[{0}:]**".format("Estampa de tiempo"))

                col1, col2 = st.columns(2)

                date_ini = col1.date_input("Fecha de Inicio:")
                date_end = col2.date_input("Fecha Final:")
        
        options = funTap1.get_expander_params(list_show_output=[key for key in dict_parameters])

        submittedTab1 = st.form_submit_button("Aceptar")

        if submittedTab1:
            if dataEntryOptions == selectDataEntryOptions[0]:
                if latitude is not None and longitude is not None:
                    st.session_state['dict_params'] = {
                        "latitude": latitude,
                        "longitude": longitude,
                        "start": date_ini,
                        "end": date_end
                        }
                else:
                    st.warning("Ingrese una latitud y longitud en el mapa interactivo", icon="⚠️")
 
            elif dataEntryOptions == selectDataEntryOptions[1]:
                if coordinate_options == selectCoordinateOptions[0]:
                    st.session_state['dict_params'] = funTap1.GMS_2_GD({
                        "lat_NS": NS,
                        "lat_degrees": lat_degrees,
                        "lat_minutes": lat_minutes,
                        "lat_seconds": lat_seconds,
                        "lon_EO": EO,
                        "lon_degrees": lon_degrees,
                        "lon_minutes": lon_minutes,
                        "lon_seconds": lon_seconds,
                        "date_ini": date_ini,
                        "date_end": date_end,
                        })
                        
                elif coordinate_options == selectCoordinateOptions[1]:
                    st.session_state['dict_params'] = {
                        "latitude": lat_input,
                        "longitude": lon_input,
                        "start": date_ini,
                        "end": date_end
                        }
                    
                elif dataEntryOptions == selectDataEntryOptions[2]:
                    if uploadedFileYaml is not None:
                        try:
                            st.session_state['dict_params'] = yaml.safe_load(uploadedFileYaml)

                        except:
                            st.error("Error al cargar archivo **YAML** (.yaml)", icon="🚨")
                    else:
                        st.warning("Cargar archivo **YAML** (.yaml)", icon="⚠️")

                
    if st.session_state['dict_params'] is not None:   
        dict_params = st.session_state['dict_params']
        cal_rows = funTap1.cal_rows(dict_params["start"], dict_params["end"], steps=60)

        if len(options) != 0:
            if cal_rows > 0:
                parameters = funTap1.get_parameters_NASA_POWER(options, dict_parameters)
                    
                data = funTap1.get_dataframe_NASA_POWER(dict_params,
                                                        parameters,
                                                        dict_parameters)
                    
                data = funTap1.add_column_dates(dataframe=data,
                                                date_ini=dict_params["start"],
                                                rows=cal_rows,
                                                steps=60)
                
                sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 Parámetros", "📈 Gráficas", "💾 Descargas"])

                with sub_tab1:
                    with st.container(border=True):
                        st.dataframe(data)

                with sub_tab2:
                    with st.container(border=True):
                        funTap1.view_dataframe_information(data)

                with sub_tab3:
                    excel = funTap1.to_excel(data)
                    buffer_params = funTap1.get_bytes_yaml(dictionary=dict_params)

                    with st.container(border=True):
                        st.download_button(
                            label="📄 Descargar **:blue[Datos climaticos y potencial energético del sitio]** del sitio **XLSX**",
                            data=excel,
                            file_name=funTap1.name_file_head(name="PES_params.xlsx"),
                            mime="xlsx")
                            
                        st.download_button(
                            label="📌 Descargar **:blue[archivo de datos]** del sitio **YAML**",
                            data=buffer_params,
                            file_name=funTap1.name_file_head(name="PES_data.yaml"),
                            mime="text/yaml")
                    
                
            else:
                if cal_rows == 0:
                    st.warning("La {0} debe ser diferente a la {1}".format(":blue[Fecha de Inicio]", ":blue[Fecha final]"), icon="⚠️")
                if cal_rows < 0:
                    st.warning("La {0} debe ser menor a la {1}".format(":blue[Fecha de Inicio]", ":blue[Fecha final]"), icon="⚠️")
        else:
            st.warning("Ingrese por lo menos una opción en {0}".format(":blue[Seleccione los datos a cargar]"), icon="⚠️")
            
    return
        
def tab2():
    st.header(list_tabs[1])

    with st.container(border=True):
        label_Gef_Tamb = "Cargar archivo {0} y {1}".format("**Irradiancia efectiva** (m/s)", "**Temperatura ambiente** (°C).")
        archive_Gef_Tamb = st.file_uploader(label=label_Gef_Tamb, type={"xlsx"})

        funTap2.get_download_button(**template)

    inputNOCT = funTap2.get_widget_number_input(label=funTap2.get_label_params(dict_param=NOCT),
                                           variable=NOCT["number_input"])
    
    app_submitted_2 = st.button("Aceptar", key="app_submitted_2")

    if app_submitted_2:
        if archive_Gef_Tamb is not None:
            check = False
            try:
                df_input = pd.read_excel(archive_Gef_Tamb)
                df_input, check, columns_options_sel = funTap2.check_dataframe_input(dataframe=df_input, options=dict_parameters)
            except:
                st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")

            if check:
                df_output = funTap2.get_column_Toper(dataframe=df_input,
                                                     options_sel=columns_options_sel,
                                                     NOCT=inputNOCT,
                                                     column_name="Toper(°C)")
                
                sub_tab1, sub_tab2 = st.tabs(["📋 Parámetros", "💾 Descargas"])

                with sub_tab1:
                    with st.container(border=True):
                        st.dataframe(df_output)

                with sub_tab2:
                    excel = funTap2.to_excel(df_output)

                    with st.container(border=True):
                        st.download_button(
                            label="📄 Descargar **:blue[Temperatura de operación del módulo]** del sitio **XLSX**",
                            data=excel,
                            file_name=funTap2.name_file_head(name="PES_addToper.xlsx"),
                            mime="xlsx")

            else:
                st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")
        else:
            st.warning("Cargar archivo **Excel** (.xlsx)", icon="⚠️")

    return

def tab3():
    st.header(list_tabs[2])
    
    uploaded_file = st.file_uploader("Cargar archivo original", type=["xlsx"])
    if uploaded_file is not None:
        df_excel = pd.read_excel(uploaded_file)

        st.dataframe(df_excel)

        variation = st.slider("Seleccione el rango en que variarán los datos (%):", min_value=1, max_value=30) / 100
        delta_time_m = st.selectbox("Seleccione el intervalo de tiempo en minutos:", options=[5, 10, 15, 30])

        opciones_validas = funTap3.valid_options(df_excel, dict_parameters)

        # [C] función que ni idea que hace pero no hace nada XD
        funTap3.valid_options(df_excel, dict_parameters)

        # Mostrar selector para columnas a procesar
        data_columns = st.multiselect("Seleccione las columnas a procesar:", opciones_validas, default=opciones_validas)

        n_samples = 60 // delta_time_m

        # Procesar el archivo
        if st.button("Procesar Datos"):
            out = funTap3.create_dataframe_nsamples(df_excel, n_samples)
            out = funTap3.modify_time_interval(out, delta_time_m)
            
            # Procesar datos y crear el archivo de salida
            output_filename = uploaded_file.name.replace(".xlsx", f"_intervalo_de_{delta_time_m}_min.xlsx")
            funTap3.process_data(df_excel, data_columns, out)

            # Descargar el archivo procesado
            excel_bytes_io = io.BytesIO()
            out.to_excel(excel_bytes_io, index=False)
            excel_bytes_io.seek(0)
            
            st.download_button(label="Descargar archivo procesado",
                               data=excel_bytes_io.read(),
                               file_name=output_filename)

            st.success(f"Datos procesados y guardados en '{output_filename}'.")

    return

pg = st.navigation([
    st.Page(tab1, title=list_tabs[0]),
    st.Page(tab2, title=list_tabs[1]),
    st.Page(tab3, title=list_tabs[2]),
])
pg.run()
