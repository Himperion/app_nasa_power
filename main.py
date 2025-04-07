import streamlit as st
import pandas as pd
import numpy as np
import folium, warnings, io, yaml
import matplotlib.pyplot as plt

from streamlit_folium import st_folium
from datetime import date, timedelta
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

dateImputNasa = {
    "min_value": date.today() - timedelta(days=251),
    "max_value": date.today() - timedelta(days=250),
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

                date_ini = col1.date_input("Fecha de Inicio:", max_value=dateImputNasa["min_value"], )
                date_end = col2.date_input("Fecha Final:", max_value=dateImputNasa["max_value"])

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

    archive_Gef_Tamb = None

    st.header(list_tabs[1])

    tab_info, tab_main = st.tabs(["📑 Información", "📝 Entrada de datos"])

    with tab_info:
        st.markdown("Determinar la temperatura de operación de los módulos fotovoltaicos permite realizar un análisis más preciso de su desempeño. Esta temperatura puede calcularse mediante la siguiente expresión matemática.")
        st.latex(r"T_{oper}=T_{amb}+G_{eff}*\frac{NOCT-20°C}{800W*m^{2}}")

        st.markdown("**Toper:** Temperatura de operación del módulo fotovoltaico (°C).")
        st.markdown("**Tamb:** Temperatura ambiente del sitio (°C).")
        st.markdown("**Geff:** Irradiancia efectiva (W/m²)." )
        st.markdown("**NOCT:** Temperatura de operación nominal de la celda (*Nominal Operating Cell Temperature*) (°C)." )

        st.divider()
        
        with st.form("formExampleToper", border=True):
            st.markdown("🧮 **:blue[Ejemplo]**")
            col1, col2, col3, col4 = st.columns(4, vertical_alignment="bottom")

            with col1:
                TambExample = st.number_input("**Tamb (°C)**", min_value=-20.0, max_value=70.0, value=38.0, step=None)
            with col2:
                GeffExample = st.number_input("**Geff (W/m²)**", min_value=0.0, max_value=1000.0, value=1000.0, step=None)
            with col3:
                NOCT_Example = st.number_input("**NOCT (°C)**", min_value=20.0, max_value=55.0, value=42.0, step=None)
            with col4:
                submittedExampleToper = st.form_submit_button("Calcular")

            if submittedExampleToper:
                ToperExample = TambExample + GeffExample*((NOCT_Example-20)/800)
                st.markdown(f"**Toper(°C) = :blue[{ToperExample}]**")

        st.divider()

        st.markdown("La pestaña **:blue[📝 Entrada de datos]** automatiza el cálculo de la temperatura de operación para una gran cantidad de datos de irradiancia efectiva y temperatura ambiente del sitio.")

    with tab_main:
        with st.container(border=True):
            label_Gef_Tamb = "Cargar archivo {0} y {1}".format("**Irradiancia efectiva** (W/m²)", "**Temperatura ambiente** (°C).")
            archive_Gef_Tamb = st.file_uploader(label=label_Gef_Tamb, type={"xlsx"})

            funTap2.get_download_button(**template)

        if archive_Gef_Tamb is not None:
            check = False
            try:
                df_input = pd.read_excel(archive_Gef_Tamb)
                df_input, check, columns_options_sel = funTap2.check_dataframe_input(dataframe=df_input, options=items_options_columns_df)
            except:
                st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")

            if check:
                with st.form("formTab2", border=True):
                    inputNOCT = funTap2.get_widget_number_input(label=funTap2.get_label_params(dict_param=NOCT),
                                                                variable=NOCT["number_input"])
                    
                    submitted_formTab2 = st.form_submit_button("Aceptar")

                if submitted_formTab2:
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

    tab_info, tab_main = st.tabs(["📑 Información", "📝 Entrada de datos"])

    with tab_info:
        st.markdown("Partiendo de un par de puntos consecutivos $(x_{i}, y_{i})$ y $(x_{i+1}, y_{i+1})$, y deseando agregar $n$ puntos equidistantes en el intervalo $x_{i}$  y $x_{i+1}$, con el fin de aumentar el número de muestras.")
        st.latex(r"\Delta x=\frac{x_{i+1}-x_{i}}{n}")
        st.markdown("Los nuevos valores en el eje $x$ generados serán:")
        st.latex(r"x_{j}=x_{i}+(1-j)\Delta x")
        st.latex(r"j: 1, 2,...,n")
        st.markdown("Ahora para los respectivos valores en el eje y se propone agregar cierta variabilidad límite máxima y límite mínima como factor del valor original:")
        st.latex(r"var_{max}=(k+1)y_{i}")
        st.latex(r"var_{min}=(k-1)y_{i}")
        st.latex(r"0< k <1")
        st.markdown("Con esta consideración, los nuevos valores se mantendrán en el límite de rango de variación. Como ejemplo para el primer valor objetivo:")
        st.latex(r"y_{1}=var_{min}< y_{i} < var_{max}")

        col1, col2, col3 = st.columns( [0.25, 0.5, 0.25])
        with col1:
            st.write("")
        with col2:
            st.image("files//img_tab4_1.png")
        with col3:
            st.write("")

        st.markdown("Para mantener un sentido lógico con el valor original se plantea, el promedio de los datos objetivo sea aproximadamente igual al valor del origen.")
        st.latex(r"y_{i}\cong \frac{y_{1}+y_{2}+...+y_{n}}{n}=mean(y_{1},y_{2},...,y_{n})")
        st.markdown("Esta expresión nos permitirá obtener una función de coste ($CF$) que permita evaluar los valores objetivo ($y_{1},y_{2},...,y_{n}$).")
        st.latex(r"CF=(y_{i}-mean(y_{1},y_{2},...,y_{n}))^{2}")
        st.markdown("Ahora para poder actualizar los valores objetivos es necesaria la derivada parcial de la función de coste en función del valor de interés a actualizar $mean(y_{1},y_{2},...,y_{n})$")
        st.latex(r"CF^{'}=2(mean(y_{1},y_{2},...,y_{n})-y_{i})")
        st.markdown("Y actualizamos el valor mediante la siguiente expresión de predicción:")
        st.latex(r"pre(y_{1},y_{2},...,y_{n})=(y_{1},y_{2},...,y_{n})-\alpha *CF")
        st.markdown(r"$\alpha$: Tasa de aprendizaje")
        st.markdown("Para medir objetivamente que el valor generado sea aceptable se define el error como la función de coste ($CF$) evaluada en la predicción ($pre(y_{1},y_{2},...,y_{n})$):")
        st.latex(r"err=CF(y_{1},y_{2},...,y_{n})")
        st.markdown("**A grandes rasgos el algoritmo se resume en los siguientes pasos:**")
        st.markdown("1.	Plantear una tolerancia máxima, numero de iteraciones máximas como condiciones de parada y la tasa de aprendizaje.")
        st.markdown("2.	Inicializar los valores $y_{1},y_{2},...,y_{n}$ con datos aleatorios entre $var_{min}$ y $var_{max}$.")
        st.markdown("3.	Evaluar la derivada de la función de coste $CF^{'}(y_{1},y_{2},...,y_{n})$.")
        st.markdown("4.	Obtener la predicción $pre(y_{1},y_{2},...,y_{n})$")
        st.markdown("5.	Evaluar la predicción en la función de coste $CF$ para obtener el error.")
        st.markdown("6.	Repetir desde el paso 3 actualizando los valores $y_{1},y_{2},...,y_{n}$ con la predicción mientras no se cumplan las condiciones de parada.")

        st.divider()

        with st.form("formExampleCF", border=True):
            st.markdown("🧮 **:blue[Ejemplo]**")
            col1, col2 = st.columns(2)

            with col1:
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        xi = st.number_input("**$x_{i}$:**", min_value=0, max_value=3, value=1, step=1)
                    with c2:
                        yi = st.number_input("**$y_{i}$:**", min_value=0, max_value=5, value=2, step=1)
            with col2:
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        xi_1 = st.number_input("**$x_{i+1}$:**", min_value=4, max_value=10, value=5, step=1)
                    with c2:
                        yi_1 = st.number_input("**$y_{i+1}$:**", min_value=0, max_value=6, value=3, step=1)

            c1, c2 = st.columns(2)

            with c1:
                n = st.slider("**$n$:**", min_value=1, max_value=10, value=4, step=1)
            with c2:
                var = st.slider("**$var$:**", min_value=0.1, max_value=0.9, value=0.2, step=0.1)

            with st.container(border=True):
                c1, c2 = st.columns(2)
                with c1:
                    tol = st.selectbox("**Tolerancia:**", options=[0.01, 0.001, 0.0001], index=1)
                with c2:
                    iter = st.selectbox("**número de iteraciones máximas:**", options=[100, 1000, 10000], index=1)

            submittedCF = st.form_submit_button("Calcular")
            
            if submittedCF:
                dictExampleCF = {
                    "xi": xi,
                    "xi_1": xi_1,
                    "yi": yi,
                    "yi_1": yi_1,
                    "n": n,
                    "var": var,
                    "tol": tol,
                    "iter": iter
                }
                

                xj, yj, mean_yj, iter_count, err_values, var_min, var_max = funTap3.exampleCF(**dictExampleCF)

                tab1, tab2, tab3 = st.tabs(["Resumen de resultados", "Gráfica de puntos generados", "Gráfica de evolución del error"])

                with tab1:
                    c1, c2 = st.columns([0.45, 0.55])

                    with c1:
                        with st.container(border=True):
                            st.markdown("📈 **Puntos generados:**")
                            for i in range(0,len(xj),1):
                                st.markdown(f"**(x{i+1}, y{i+1})** = ({xj[i]}, {yj[i]})")
                    with c2:
                        with st.container(border=True):
                            st.markdown("📝 **Información de la ejecución del algoritmo:**")
                            st.markdown(f"Número de iteraciones = {iter_count}")
                            st.markdown("$mean(y_{1},y_{2},...,y_{n})$="+f"{mean_yj}")
                            st.markdown("$err$="+f"{err_values[-1]}")

                with tab2:
                    with st.container(border=True):
                        fig, ax = plt.subplots()

                        ax.scatter(xj, yj, color="red", label="puntos generados")
                        ax.scatter(xi, yi, color="blue", label="$(x_{i}, y_{i})$")
                        ax.scatter(xi_1, yi_1, color="purple", label="$(x_{i+1}, y_{i+1})$")
                        ax.plot([xi, xi_1], [mean_yj, mean_yj], color="green", linestyle='--', label="$mean(y_{1},y_{2},...,y_{n})$")
                        ax.plot([xi, xi_1], [var_min, var_min], color="cyan", linestyle='--', label="$var_{min}$")
                        ax.plot([xi, xi_1], [var_max, var_max], color="navy", linestyle='--', label="$var_{max}$")

                        for i in range(len(xj)):
                            ax.text(xj[i], yj[i], f"({round(xj[i], 3)}, {round(yj[i], 3)})", fontsize=6, ha="left", va='bottom')

                        ax.set_xlabel('Valores de X')
                        ax.set_ylabel('Valores de Y')
                        ax.legend()
                        ax.grid(True)

                        st.pyplot(fig)

                with tab3:
                    with st.container(border=True):
                        fig, ax = plt.subplots()

                        x = np.array([i for i in range(0, iter_count, 1)])
                        y = np.array(err_values)

                        ax.scatter(x, y, color="blue", label="$err$")
                        ax.plot(x, y, color="navy", linestyle='--', label="Tendencia del error")

                        for i in range(len(x)):
                            ax.text(x[i], y[i], f"({x[i]}, {round(y[i], 6)})", fontsize=6, ha="left", va='bottom')

                        ax.set_xlabel('Número de iteraciones')
                        ax.set_ylabel("Evolución del error")
                        ax.legend()
                        ax.grid(True)

                        st.pyplot(fig)

    with tab_main:
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
