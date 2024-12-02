import streamlit as st
import pandas as pd
import folium, warnings, io
from streamlit_folium import st_folium
from pynasapower.get_data import query_power
from pynasapower.geometry import point
from datetime import datetime, timedelta
import random
import numpy as np
from folium.plugins import MousePosition

warnings.filterwarnings("ignore")

# Inicializar session_state
if 'form1_accept' not in st.session_state:
    st.session_state.form1_accept = False

# Funciones

def name_file_head(name: str) -> str:
    now = datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def cal_rows(date_ini, date_end, steps):
    date_delta = date_end - date_ini
    cal_rows = int((date_delta.days * 1440)/steps)
    return cal_rows

def get_parameters_NASA_POWER(options: list) -> list:
    parameters = []
    for i in range(0, len(options), 1):
        parameters.append(dict_parameters[options[i]][0])
    return parameters

def get_dataframe_NASA_POWER(latitude, longitude, start, end, parameters) -> pd.DataFrame:
    dataframe = query_power(geometry=point(x=longitude, y=latitude, crs="EPSG:4326"),
                            start=start,
                            end=end,
                            to_file=False,
                            community="re",
                            parameters=parameters,
                            temporal_api="hourly",
                            spatial_api="point")

    list_columns, list_columns_drop = list(dataframe.columns), ["YEAR", "MO", "DY", "HR"]

    for i in range(0, len(list_columns_drop), 1):
        if list_columns_drop[i] in list_columns:
            dataframe = dataframe.drop(columns=[list_columns_drop[i]])

    for key in dict_parameters:
        if dict_parameters[key][0] in list_columns:
            dataframe = dataframe.rename(columns={dict_parameters[key][0]: dict_parameters[key][1]})

    return dataframe

def add_column_dates(dataframe, date_ini, rows, steps):
    list_columns = list(dataframe.columns)
    if not "dates (Y-M-D hh:mm:ss)" in list_columns:
        dates = pd.date_range(start=date_ini,
                              periods=rows,
                              freq=pd.Timedelta(minutes=steps))

        if dataframe.shape[0] >= dates.shape[0]:
            dataframe = dataframe.head(rows)

        if dataframe.shape[0] == dates.shape[0]:
            dataframe["dates (Y-M-D hh:mm:ss)"] = dates
            dataframe = dataframe[["dates (Y-M-D hh:mm:ss)"] + list_columns]

    return dataframe

def get_list_tabs_graph(list_data_columns, list_options_columns_name, list_options_columns_label):
    list_tabs_graph_name, list_tabs_graph_label = [], []
    for i in range(0, len(list_data_columns), 1):
        if list_data_columns[i] in list_options_columns_name:
            list_tabs_graph_name.append(list_data_columns[i])
            list_tabs_graph_label.append(list_options_columns_label[list_options_columns_name.index(list_data_columns[i])])

    return list_tabs_graph_name, list_tabs_graph_label

def view_dataframe_information(dataframe):
    list_options_columns_name = ["Load(W)",
                                 "Gin(W/m²)",
                                 "Tamb 2msnm(°C)",
                                 "Vwind 10msnm(m/s)",
                                 "Vwind 50msnm(m/s)"]

    list_options_columns_label = ["💡 Load(W)",
                                  "🌤️ Gin(W/m²)",
                                  "🌡️ Tamb 2msnm(°C)",
                                  "✈️ Vwind 10msnm(m/s)",
                                  "✈️ Vwind 50msnm(m/s)"]

    list_data_columns = list(dataframe.columns)

    list_tabs_graph_name, list_tabs_graph_label = get_list_tabs_graph(list_data_columns,
                                                                     list_options_columns_name,
                                                                     list_options_columns_label)

    tab_con1, tab_con2 = st.tabs(["📄 Tabla", "📈 Gráficas"])

    with tab_con1:
        st.dataframe(dataframe)
    with tab_con2:
        if len(list_tabs_graph_name) != 0:
            if len(list_tabs_graph_name) == 1:
                subtab_con1 = st.tabs(list_tabs_graph_label)
                list_subtab_con = [subtab_con1[0]]
            elif len(list_tabs_graph_name) == 2:
                subtab_con1, subtab_con2 = st.tabs(list_tabs_graph_label)
                list_subtab_con = [subtab_con1, subtab_con2]
            elif len(list_tabs_graph_name) == 3:
                subtab_con1, subtab_con2, subtab_con3 = st.tabs(list_tabs_graph_label)
                list_subtab_con = [subtab_con1, subtab_con2, subtab_con3]
            elif len(list_tabs_graph_name) == 4:
                subtab_con1, subtab_con2, subtab_con3, subtab_con4 = st.tabs(list_tabs_graph_label)
                list_subtab_con = [subtab_con1, subtab_con2, subtab_con3, subtab_con4]

            for i in range(0, len(list_subtab_con), 1):
                with list_subtab_con[i]:
                    st.line_chart(data=dataframe[[list_tabs_graph_name[i]]], y=list_tabs_graph_name[i])

    return

# Funciones adicionales para el procesamiento de datos
constants_GD = {
    "alpha": 0.1,
    "tol": 0.001,
    "iter_max": 1000
}

def gradient_descent_LR(value, n, variation, alpha, tol, iter_max):
    err, iter_count = 100, 0
    if np.any(value == 0.0):
        return np.zeros(n)
    else:
        range_min, range_max = value * (1 - variation), value * (1 + variation)
        xi = np.array([random.uniform(range_min, range_max) for i in range(n)])
        while iter_count < iter_max and err > tol:
            dL_xi = (2 / n) * (np.mean(xi) - value)
            xi_predict = xi - alpha * dL_xi
            err = abs(np.mean(xi_predict) - value)
            xi = xi_predict
            iter_count += 1
        return xi_predict

def crear_dataframe_nsamples(org, n_samples):
    out = pd.DataFrame()
    for col in org.columns:
        out[col] = org[col].repeat(n_samples).reset_index(drop=True)
    return out

def modificar_inter_tiempo(out:pd.DataFrame, delta_time_m:int):
    if "dates (Y-M-D hh:mm:ss)" in list(out.columns):
        out["dates (Y-M-D hh:mm:ss)"] = pd.to_datetime(out["dates (Y-M-D hh:mm:ss)"] )
        increment = timedelta(minutes=delta_time_m)
        for index, row in out.iterrows():
            if index == 0:
                last_time = row["dates (Y-M-D hh:mm:ss)"]
            else: 
                last_time += increment
                out.at[index,"dates (Y-M-D hh:mm:ss)"]=last_time
    return out

def aplicar_gradient(row):
    new_rows = []
    values_predict = {datos: gradient_descent_LR(value=row[datos], n=n_samples, variation=variation, **constants_GD) for datos in datos_columnas}
    for i in range(n_samples):
        new_row = [round(values_predict[datos][i], 4) for datos in datos_columnas]
        new_rows.append(new_row)
    return new_rows

def procesar_datos(org, aplicar_gradient, datos_columnas, out):
    aux = []
    aux = np.vstack(org.apply(aplicar_gradient, axis=1).explode().to_numpy())
    aux_df = pd.DataFrame(aux, columns=datos_columnas)
    common_columns = aux_df.columns.intersection(out.columns)
    out[common_columns] = aux_df[common_columns]
    return out
    



# Main

dict_parameters = {
    "Irradiancia (W/m^2)": ("ALLSKY_SFC_SW_DWN", "Gin(W/m²)"),
    "Velocidad del viento a 10 msnm (m/s)": ("WS10M", "Vwind 10msnm(m/s)"),
    "Velocidad del viento a 50 msnm (m/s)": ("WS50M", "Vwind 50msnm(m/s)"),
    "Temperatura ambiente a 2 msnm (°C)": ("T2M", "Tamb 2msnm(°C)")
}

options_multiselect = list(dict_parameters.keys())

latitude, longitude, data_dates = None, None, None

tab1, tab2 = st.tabs(["Datos Climáticos", "Cambiar intervalo de tiempo"])

with tab1:
    st.header(":mostly_sunny: Datos climáticos y potencial energético del sitio", divider=True)

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

    with st.form('form_1'):
        col1, col2 = st.columns([0.5, 0.5])

        date_ini = col1.date_input("Fecha de Inicio:")
        date_end = col2.date_input("Fecha Final:")

        options = st.multiselect("Seleccione los datos a cargar:",
                                 options=options_multiselect,
                                 placeholder="Seleccione una opción",
                                 default=options_multiselect[0])
        
        form_1_submitted = st.form_submit_button("Aceptar")

        if form_1_submitted:
            if latitude is not None and longitude is not None:
                if len(options) != 0:
                    cal_rows = cal_rows(date_ini, date_end, steps=60)
                    if cal_rows > 0:
                        parameters = get_parameters_NASA_POWER(options)

                        data = get_dataframe_NASA_POWER(latitude=latitude,
                                                        longitude=longitude,
                                                        start=date_ini,
                                                        end=date_end,
                                                        parameters=parameters)

                        data_dates = add_column_dates(dataframe=data,
                                                      date_ini=date_ini,
                                                      rows=cal_rows,
                                                      steps=60)
                        
                        with st.container():
                            view_dataframe_information(data_dates)

                        st.session_state.form1_accept = True
                    else:
                        st.warning("La {0} debe ser diferente a la {1}".format(":blue[Fecha de Inicio]", ":blue[Fecha final]"), icon="⚠️")
                else:
                    st.warning("Ingrese por lo menos una opción en :blue[Seleccione los datos a cargar]", icon="⚠️")
            else:
                st.warning("Ingrese una latitud y longitud en el mapa interactivo", icon="⚠️")

            
    if st.session_state.form1_accept and data_dates is not None:
        excel_bytes_io = io.BytesIO()
        data_dates.to_excel(excel_bytes_io, index=False)
        excel_bytes_io.seek(0)

        st.download_button(label="Descargar archivo",
                           data=excel_bytes_io.read(),
                           file_name=name_file_head("ALLSKY_SFC_SW_DWN.xlsx"))

 

with tab2:
    st.header("Cargar archivo para variar el intervalo de tiempo")
    
    # Cargar archivo .xlsx
    uploaded_file = st.file_uploader("Cargar archivo original", type=["xlsx"])
    if uploaded_file is not None:
        # Leer el archivo Excel en un DataFrame de pandas
        df = pd.read_excel(uploaded_file)

        # Mostrar el contenido del archivo
        st.write("Contenido del archivo cargado:")
        st.dataframe(df)

        # Parámetros de usuario para el procesamiento
        variation = st.slider("Seleccione el rango en que variarán los datos (%):", min_value=1, max_value=30) / 100
        delta_time_m = st.selectbox("Seleccione el intervalo de tiempo en minutos:", options=[5, 10, 15, 30])

        # Filtrar opciones válidas basadas en dict_parameters
        opciones_validas = [v[1] for k, v in dict_parameters.items() if v[1] in df.columns.tolist()]

        # Mostrar selector para columnas a procesar
        datos_columnas = st.multiselect("Seleccione las columnas a procesar:", opciones_validas, default=opciones_validas)

        n_samples = 60 // delta_time_m

        # Procesar el archivo
        if st.button("Procesar Datos"):
            out = crear_dataframe_nsamples(df, n_samples)
            out = modificar_inter_tiempo(out, delta_time_m)
            
            # Procesar datos y crear el archivo de salida
            output_filename = uploaded_file.name.replace(".xlsx", f"_intervalo_de_{delta_time_m}_min.xlsx")
            procesar_datos(df, aplicar_gradient, datos_columnas, out)

            # Descargar el archivo procesado
            excel_bytes_io = io.BytesIO()
            out.to_excel(excel_bytes_io, index=False)
            excel_bytes_io.seek(0)
            
            st.download_button(label="Descargar archivo procesado",
                               data=excel_bytes_io.read(),
                               file_name=output_filename)

            st.success(f"Datos procesados y guardados en '{output_filename}'.")
