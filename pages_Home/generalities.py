# -*- coding: utf-8 -*-
import streamlit as st
import qrcode
from io import BytesIO

text = {
    "subheader_1" : "Implementación del proyecto **Diseño de un aplicativo para la estimación de la operación de sistemas de generación eléctrica a partir de balances de potencia y energía**"
}

# st.markdown("# :material/home: Inicio")

st.markdown("# :material/partly_cloudy_day: Datos climáticos y consumo eléctrico")

tab1, tab2 = st.tabs([":material/ink_pen: Descripción", ":material/groups: Equipo humano"])

with tab1:
    # st.markdown(text["subheader_1"])
    # st.link_button(":orange-badge[**Presentación TdeG**]", "https://www.canva.com/design/DAGmHexFq7U/mIh7Px5eheIPUwhtWkfnmw/edit?utm_content=DAGmHexFq7U&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton", icon="👨‍🏫")

    # st.title("Herramientas de caracterización")
    st.markdown("Aplicación web diseñada para la ayuda en **caracterización de proyectos de generación eléctrica**, esta permite analizar y obtener información espacio-temporal de variables climáticas y de consumo eléctrico. Los datos resultantes se consolidan en un archivo **Excel** esencial para las siguientes fases de estudio.")

    
    with st.container(border=True):
        st.header(":material/qr_code_2: **Código QR de la aplicación**", divider="yellow")

        url = "https://app-nasa-power.streamlit.app/"
        qr = qrcode.make(url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)

        st.image(buffer.getvalue(), width=250)

    with st.container(border=True):
        st.header(":material/partly_cloudy_day: **Datos climáticos y potencial energético**", divider="yellow")
        st.markdown("Esta sección permite obtener lecturas horarias de variables climáticas clave como la **irradiancia**, **temperatura ambiente**, y la **velocidad y dirección del viento**. Estas lecturas provienen del sistema **NASA POWER** (Prediction Of Worldwide Energy Resources), que genera sus datos mediante la combinación de **observaciones satelitales** y **modelos matemáticos** de asimilación global.")
        st.markdown("<p style='font-size: 0.9em; color: gray;'>🔗<a href='https://power.larc.nasa.gov/' target='_blank'>NASA POWER</a></p>", unsafe_allow_html=True)

    with st.container(border=True):
        st.header(":material/electrical_services: **Consumo eléctrico**", divider="yellow")
        st.markdown("Esta funcionalidad permite la **incorporación de perfiles de carga eléctrica** basados en plantillas predeterminadas o definidos por el usuario.")

with tab2:

    with st.container(border=True):
        col1, col2 = st.columns([0.3, 0.7], vertical_alignment="center")

        with col1:
            st.image("files/HOME/member2.jpg", width=200)

        with col2:
            st.subheader("Darío Fernando Gonzalez Fontecha", divider="yellow")
            st.caption("Comprometido con el desarrollo sostenible, energias renovables y la implementación de tecnologías innovadoras para el sector agropecuario. Con conocimientos en MATLAB, Python y desarrollo Web, oriento mis habilidades hacia el uso de Big Data y computación en la nube para transformar el campo colombiano.")
            st.markdown(":material/mail: dario.gonzalez@correo.uis.edu.co")

    with st.container(border=True):
        col1, col2 = st.columns([0.3, 0.7], vertical_alignment="center")

        with col1:
            st.image("files/HOME/member1.jpg", width=200)

        with col2:
            st.subheader("José Camilo Rojas Páez", divider="yellow")
            st.caption("Ingeniero electricista de la Universidad Industrial de Santander, con una sólida base en matemáticas y lógica de programación aplicadas a la resolución de problemas. Experiencia en el uso de herramientas de software y programación, como MATLAB, Python, Streamlit y Power BI, para el análisis y procesamiento de datos.")
                
            st.markdown(":material/mail: jose.rojas9@correo.uis.edu.co")
            # st.markdown("🐈‍⬛ https://github.com/Himperion")

    with st.container(border=True):
        col1, col2 = st.columns([0.3, 0.7], vertical_alignment="center")

        with col1:
            st.image("files/HOME/member3.jpg", width=200)

        with col2:
            st.subheader("German Alfonso Osma Pinto", divider="yellow")
            st.caption("Investigador Senior MINCIENCIAS y miembro del Grupo de Investigación en Sistemas de Energía Eléctrica Eléctrica – GISEL. Cuenta con más de 10 años de experiencia docente en pregrado y posgrado. Ha participado en diversos proyectos con financiación MINCIENCIAS y UIS. Lleva más de 15 años en el quehacer investigativo relacionado con la generación renovable y construcción sostenible. Actualmente, apoya el Semillero de Investigación en Recursos Energéticos Distribuidos - SIRED.")
            st.markdown(":material/mail: gealosma@uis.edu.co")