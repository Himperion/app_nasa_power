import streamlit as st
import pandas as pd
import folium, warnings, io, yaml
from streamlit_folium import st_folium

from funtions import funTap1, funTap2, funTap3, funTap4

warnings.filterwarnings("ignore")

#%% cache_data

@st.cache_data
def get_outForm4(dict_params, constants_GD):

    n_samples = 60 // dict_params['deltaTime_m']

    out = funTap3.create_dataframe_nsamples(dict_params['df_excel'], n_samples)
    out = funTap3.modify_time_interval(out, dict_params['deltaTime_m'])
    out = funTap3.process_data(out, n_samples, dict_params, constants_GD)
    excel_bytes = funTap3.get_excel_bytes(out)

    return excel_bytes

#%% global variables

with open("files//dict_parameters.yaml", 'r') as archivo:
    dict_parameters = yaml.safe_load(archivo)

items_options_columns_df = {
    "Geff" : ("Gef(W/m^2)", "Gef(W/m²)", "Gin(W/m²)", "Gin(W/m^2)"),
    "Tamb" : ("Tamb(°C)", "Tamb 2msnm(°C)")
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

if 'dict_paramsForm1' not in st.session_state:
    st.session_state['dict_paramsForm1'] = None

if 'dict_paramsForm3' not in st.session_state:
    st.session_state['dict_paramsForm3'] = None

if 'dict_paramsForm4' not in st.session_state:
    st.session_state['dict_paramsForm4'] = None

options_multiselect = list(dict_parameters.keys())

list_tabs = [
    "🌤️ Datos climáticos y potencial energético",
    "🌡️ Temperatura de operación",
    "🔌 Consumo eléctrico",
    "⏱️ Aumentar número de muestras"
    ]

selectDataEntryOptions = [
    "🗺️ Mapa interactivo",
    "📌 Datos del sitio",
    "💾 Cargar archivo de datos del sitio YAML"
    ]

selectCoordinateOptions = [
    "Sistema sexagesimal GMS",
    "Sistema decimal GD"
    ]

latitude, longitude, data_dates = None, None, None

def tab1():
    st.session_state['dict_paramsForm3'] = None
    st.session_state['dict_paramsForm4'] = None

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

    elif dataEntryOptions == selectDataEntryOptions[2]:
        with st.container(border=True):
            uploadedFileYaml = st.file_uploader(label="Sube tu archivo YAML", type=["yaml", "yml"])

    with st.form('form1'):
        if dataEntryOptions == selectDataEntryOptions[0] or dataEntryOptions == selectDataEntryOptions[1]:
            
            with st.container(border=True):
                st.markdown("🗓️ **:blue[{0}:]**".format("Estampa de tiempo"))

                col1, col2 = st.columns(2)

                date_ini = col1.date_input("Fecha de Inicio:")
                date_end = col2.date_input("Fecha Final:")

        parameterOptions = funTap1.get_parameterOptions(dict_parameters)
        options = funTap1.get_multiselect_params(list_show_output=parameterOptions)

        submittedTab1 = st.form_submit_button("Aceptar")

        if submittedTab1:
            if dataEntryOptions == selectDataEntryOptions[0]:
                if latitude is not None and longitude is not None:
                    st.session_state['dict_paramsForm1'] = {
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                        "start": date_ini,
                        "end": date_end
                        }
                else:
                    st.warning("Ingrese una latitud y longitud en el mapa interactivo", icon="⚠️")
 
            elif dataEntryOptions == selectDataEntryOptions[1]:
                if coordinate_options == selectCoordinateOptions[0]:
                    st.session_state['dict_paramsForm1'] = funTap1.GMS_2_GD({
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
                    st.session_state['dict_paramsForm1'] = {
                        "latitude": lat_input,
                        "longitude": lon_input,
                        "start": date_ini,
                        "end": date_end
                        }
                    
            elif dataEntryOptions == selectDataEntryOptions[2]:
                if uploadedFileYaml is not None:
                    try:
                        st.session_state['dict_paramsForm1'] = yaml.safe_load(uploadedFileYaml)

                    except:
                        st.error("Error al cargar archivo **YAML** (.yaml)", icon="🚨")
                else:
                    st.warning("Cargar archivo **YAML** (.yaml)", icon="⚠️")

                
    if st.session_state['dict_paramsForm1'] is not None:   
        dict_params = st.session_state['dict_paramsForm1']
        cal_rows = funTap1.cal_rows(dict_params["start"], dict_params["end"], steps=60)

        if len(options) != 0:
            if cal_rows > 0:
            
                dict_outForm1 = {
                    "dict_params" : dict_params,
                    "dict_parameters": dict_parameters,
                    "options": options,
                    "cal_rows": cal_rows
                }

                funTap1.get_outForm1(**dict_outForm1)
     
            else:
                if cal_rows == 0:
                    st.warning("La {0} debe ser diferente a la {1}".format(":blue[Fecha de Inicio]", ":blue[Fecha final]"), icon="⚠️")
                if cal_rows < 0:
                    st.warning("La {0} debe ser menor a la {1}".format(":blue[Fecha de Inicio]", ":blue[Fecha final]"), icon="⚠️")
        else:
            st.warning("Ingrese por lo menos una opción en {0}".format(":blue[Seleccione los datos a cargar]"), icon="⚠️")
            
    return
        
def tab2():
    st.session_state['dict_paramsForm1'] = None
    st.session_state['dict_paramsForm3'] = None
    st.session_state['dict_paramsForm4'] = None

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
                df_input, check, columns_options_sel = funTap2.check_dataframe_input(dataframe=df_input, options=items_options_columns_df)
            except:
                st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")

            if check:
                df_output = funTap2.get_column_Toper(dataframe=df_input,
                                                     options_sel=columns_options_sel,
                                                     NOCT=inputNOCT,
                                                     column_name="Toper(°C)")
                
                sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 Parámetros", "📈 Gráficas", "💾 Descargas"])

                with sub_tab1:
                    with st.container(border=True):
                        st.dataframe(df_output)

                with sub_tab2:
                    with st.container(border=True):
                        funTap2.view_dataframe_information(df_output, dict_parameters)

                with sub_tab3:
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

    st.session_state['dict_paramsForm1'] = None
    st.session_state['dict_paramsForm4'] = None

    labelUploadedYamlDATA = 'Datos climáticos y potencial energético del sitio'

    st.header(list_tabs[2])

    
    with st.form('form3'):

        col1, col2 = st.columns(2)

        with col1:
            typeLoad = st.selectbox(label='Tipo de carga', options=['Residencial', 'Comercial'], index=0)

        with col2:
            kWh_day = st.number_input(label='Consumo (kWh/día)', min_value=0.0, max_value=100.0, format='%0.3f',
                                      step=0.001, value=1.126)
            
        uploadedXlsxDATA = st.file_uploader(label=f"📋 **Cargar archivo {labelUploadedYamlDATA}**",
                                            type=["xlsx"], key='uploadedXlsxDATA')
            

        submittedTab3 = st.form_submit_button("Aceptar")

        if submittedTab3:
            if uploadedXlsxDATA is not None:
                try:
                    df_data = pd.read_excel(uploadedXlsxDATA)
                    checkTime, timeInfo = funTap3.checkTimeData(df_data, deltaMinutes=60)

                    if checkTime:
                        df_loadPU = pd.read_excel('files/[Plantilla] - CargaPU ESSA.xlsx')
                        df_data = funTap3.addLoadData(df_data, df_loadPU, typeLoad, kWh_day, timeInfo)

                        st.session_state['dict_paramsForm3'] = {
                            "df_data": df_data,
                            }

                except:
                    st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon="🚨")

            else:
                st.error(f"Cargar archivo **{labelUploadedYamlDATA}**", icon="🚨")

    if st.session_state['dict_paramsForm3'] is not None:
        df_data = st.session_state['dict_paramsForm3']['df_data']

        funTap3.get_outForm3(df_data, dict_parameters)

    return

def tab4():
    st.session_state['dict_paramsForm1'] = None
    st.session_state['dict_paramsForm3'] = None
    
    st.header(list_tabs[3])

    with st.container(border=True):
        uploaded_file = st.file_uploader("Seleccione los datos a cargar", type=["xlsx"])
        
        if uploaded_file is not None:
            try:
                df_excel = pd.read_excel(uploaded_file)

                checkTime, timeInfo = funTap3.checkTimeData(df_excel, deltaMinutes=60)

                if checkTime:
                    with st.expander(f'📄 Ver dataset **:blue[{uploaded_file.name}]**'):
                        st.dataframe(df_excel)

                    with st.form('form2'):
                        col1, col2 = st.columns(2)

                        with col1:
                            variation = st.slider("Seleccione el rango en que variarán los datos (%):", min_value=0, max_value=30) / 100
                        with col2:
                            deltaTime_m = st.selectbox("Seleccione el intervalo de tiempo en minutos:", options=[5, 10, 15, 30])

                        opciones_validas = funTap4.valid_options(df_excel, dict_parameters)

                        dataColumns = st.multiselect("Seleccione las columnas a procesar:", opciones_validas, default=opciones_validas)
                
                        submittedTab4 = st.form_submit_button("Aceptar")

                        if submittedTab4:
                            st.session_state['dict_paramsForm4'] = {
                                "df_excel": df_excel,
                                "variation": variation,
                                "deltaTime_m": deltaTime_m,
                                "dataColumns": dataColumns
                            }
                else:
                    st.error("No se encuentran columna de 'dates (Y-M-D hh:mm:ss)' o el delta de tiempo no es de 60min", icon="🚨") 

            except:
                st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon="🚨")

    if st.session_state['dict_paramsForm4'] is not None: 

        dict_paramsForm4 = st.session_state['dict_paramsForm4']
        outputFilename = f"{uploaded_file.name.split('.')[0]}_min{dict_paramsForm4['deltaTime_m']}.xlsx"

        excel_bytes = get_outForm4(dict_paramsForm4, constants_GD)

        st.download_button(label="Descargar archivo procesado",
                           data=excel_bytes.read(),
                           file_name=outputFilename)
    
    return

pg = st.navigation([
    st.Page(tab1, title=list_tabs[0]),
    st.Page(tab2, title=list_tabs[1]),
    st.Page(tab3, title=list_tabs[2]),
    st.Page(tab4, title=list_tabs[3]),
])
pg.run()
