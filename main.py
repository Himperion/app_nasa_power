# -*- coding: utf-8 -*-
import streamlit as st

pages = {
    "Inicio": [
        st.Page("pages_Home/generalities.py",  title="Generalidades", icon=":material/home:"),
        st.Page("pages_Home/resources.py",     title="Recursos",      icon=":material/laptop_windows:"),
    ],
    "Herramientas": [
        st.Page("pages_Tools/pag_ClimateData.py",            title="Datos climáticos y potencial energético", icon=":material/partly_cloudy_day:"),
        # st.Page("pages_Tools/pag_OperatingTemperature.py",   title="Temperatura de operación",                icon=":material/thermometer:"),
        st.Page("pages_Tools/pag_ElectricityConsumption.py", title="Consumo eléctrico",                      icon=":material/electrical_services:"),
        # st.Page("pages_Tools/pag_IncreaseSamples.py",        title="Aumentar número de muestras",            icon=":material/av_timer:"),
        st.Page("pages_Tools/pag_SolarPosition.py",          title="Carta solar",                            icon=":material/wb_sunny:"),
    ],
}

pg = st.navigation(pages)
pg.run()
