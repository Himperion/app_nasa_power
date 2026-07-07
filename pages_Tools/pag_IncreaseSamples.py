# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import yaml

from funtions import fun_ElectricityConsumption, funTap4, general

warnings.filterwarnings("ignore")

#%% cache_data

@st.cache_data
def get_outForm4(dict_params, constants_GD):

    n_samples = 60 // dict_params['deltaTime_m']

    out = fun_ElectricityConsumption.create_dataframe_nsamples(dict_params["df_excel"], n_samples)
    out = fun_ElectricityConsumption.modify_time_interval(out, dict_params["deltaTime_m"])
    out = fun_ElectricityConsumption.process_data(out, n_samples, dict_params, constants_GD)
    excel_bytes = general.get_excel_bytes(out)

    return excel_bytes

#%% global variables

with open(general.resource_path("files//dict_parameters.yaml"), 'r') as archivo:
    dict_parameters = yaml.safe_load(archivo)

constants_GD = {
    "alpha": 0.1,
    "tol": 0.001,
    "iter_max": 1000
}

#%% session_state

if "dict_paramsForm4" not in st.session_state:
    st.session_state["dict_paramsForm4"] = None

#%% main

st.header(":material/av_timer: **Aumentar número de muestras**")

tab_info, tab_main = st.tabs(["📑 Información", "📝 Entrada de datos"])

with tab_info:
    st.markdown(r"Partiendo de un par de puntos consecutivos $(x_{i}, y_{i})$ y $(x_{i+1}, y_{i+1})$, y deseando agregar $n$ puntos equidistantes en el intervalo $x_{i}$  y $x_{i+1}$, con el fin de aumentar el número de muestras.")
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

    col1, col2, col3 = st.columns([0.25, 0.5, 0.25])
    with col1:
        st.write("")
    with col2:
        st.image(general.resource_path("files//img_tab4_1.png"))
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
    st.markdown("1.\tPlantear una tolerancia máxima, numero de iteraciones máximas como condiciones de parada y la tasa de aprendizaje.")
    st.markdown("2.\tInicializar los valores $y_{1},y_{2},...,y_{n}$ con datos aleatorios entre $var_{min}$ y $var_{max}$.")
    st.markdown("3.\tEvaluar la derivada de la función de coste $CF^{'}(y_{1},y_{2},...,y_{n})$.")
    st.markdown("4.\tObtener la predicción $pre(y_{1},y_{2},...,y_{n})$")
    st.markdown("5.\tEvaluar la predicción en la función de coste $CF$ para obtener el error.")
    st.markdown("6.\tRepetir desde el paso 3 actualizando los valores $y_{1},y_{2},...,y_{n}$ con la predicción mientras no se cumplan las condiciones de parada.")

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
                iter_max = st.selectbox("**número de iteraciones máximas:**", options=[100, 1000, 10000], index=1)

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
                "iter": iter_max
            }

            xj, yj, mean_yj, iter_count, err_values, var_min, var_max = fun_ElectricityConsumption.exampleCF(**dictExampleCF)

            tab1_res, tab2_res, tab3_res = st.tabs(["Resumen de resultados", "Gráfica de puntos generados", "Gráfica de evolución del error"])

            with tab1_res:
                c1, c2 = st.columns([0.45, 0.55])

                with c1:
                    with st.container(border=True):
                        st.markdown("📈 **Puntos generados:**")
                        for i in range(0, len(xj), 1):
                            st.markdown(f"**(x{i+1}, y{i+1})** = ({xj[i]}, {yj[i]})")
                with c2:
                    with st.container(border=True):
                        st.markdown("📝 **Información de la ejecución del algoritmo:**")
                        st.markdown(f"Número de iteraciones = {iter_count}")
                        st.markdown("$mean(y_{1},y_{2},...,y_{n})$="+f"{mean_yj}")
                        st.markdown("$err$="+f"{err_values[-1]}")

            with tab2_res:
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

            with tab3_res:
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

                checkTime, timeInfo = fun_ElectricityConsumption.checkTimeData(df_excel, deltaMinutes=60)

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
