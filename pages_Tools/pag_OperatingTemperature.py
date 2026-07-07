# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import warnings

from funtions import funTap2, general

warnings.filterwarnings("ignore")

#%% cache_data

@st.cache_data
def get_outForm2(df, optionsSel, NOCT):

    data = funTap2.getColumnToper(df, optionsSel, NOCT)

    return data

#%% global variables

dict_downloadTap2 = funTap2.dict_download

NOCT = {
    "description": "Temperatura de operación nominal de la celda",
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

template = {
    "directory": "files",
    "name_file": "[Plantilla] - Temperatura de operación",
    "format_file": "xlsx",
    "description": "Irradiancia efectiva y Temperatura ambiente del sitio"
}

#%% session_state

if "dict_paramsForm2" not in st.session_state:
    st.session_state["dict_paramsForm2"] = None

#%% main

flag_submittedTab2 = None
archive_Gef_Tamb = None

st.header(":material/thermometer: **Temperatura de operación**")

tab_info, tab_main = st.tabs(["📑 Información", "📝 Entrada de datos"])

with tab_info:
    st.markdown("Determinar la temperatura de operación de los módulos fotovoltaicos permite realizar un análisis más preciso de su desempeño. Esta temperatura puede calcularse mediante la siguiente expresión matemática.")
    st.latex(r"T_{oper}=T_{amb}+G_{eff}*\frac{NOCT-20°C}{800W*m^{2}}")

    st.markdown("**Toper:** Temperatura de operación del módulo fotovoltaico (°C).")
    st.markdown("**Tamb:** Temperatura ambiente del sitio (°C).")
    st.markdown("**Geff:** Irradiancia efectiva (W/m²).")
    st.markdown("**NOCT:** Temperatura de operación nominal de la celda (*Nominal Operating Cell Temperature*) (°C).")

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
            df_input, check, optionsSel = funTap2.check_dataframe_input(dataframe=df_input)
        except:
            st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")

        if check:
            with st.form("formTab2", border=True):
                inputNOCT = funTap2.get_widget_number_input(label=funTap2.get_label_params(dict_param=NOCT),
                                                            variable=NOCT["number_input"])

                submitted_formTab2 = st.form_submit_button("Aceptar")

            if submitted_formTab2:
                st.session_state["dict_paramsForm2"] = {
                    "df": df_input,
                    "optionsSel": optionsSel,
                    "NOCT": inputNOCT,
                }
                flag_submittedTab2 = True

if st.session_state["dict_paramsForm2"] is not None and flag_submittedTab2:
    data = get_outForm2(**st.session_state["dict_paramsForm2"])
    general.viewInformation(data, None, dict_downloadTap2)
