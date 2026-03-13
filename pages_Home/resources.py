import streamlit as st
import streamlit.components.v1 as components

links = [

    {
        "numero": 2,
        "titulo": "COMPONENTES DE GENERACIÓN",
        "descripcion": "Permite el análisis y la parametrización operativa de diversos componentes de generación eléctrica.",
        "icono": "energy",
        "url": "https://02-elements-sired-e3t.streamlit.app/",
        "color": "#069460"
    },

    {
        "numero": 3,
        "titulo": "SISTEMAS DE GENERACIÓN v1",
        "descripcion": "Plataforma para el dimensionamiento de sistemas de generación híbridos.",
        "icono": "electric_meter",
        "url": "https://apps-energy-generation-e3t.streamlit.app/",
        "color": "#069460"
    },

    {
        "numero": 3,
        "titulo": "SISTEMAS DE GENERACIÓN v2 beta",
        "descripcion": "Plataforma para el dimensionamiento de sistemas de generación híbridos.",
        "icono": "electric_meter",
        "url": "https://04-generationsystems-sired-e3t.streamlit.app/",
        "color": "#069460"
    },

]

cards_html = ""

for link in links:

    cards_html += f"""

    <div class="card" onclick="window.open('{link['url']}')">

        <div class="grid">

            <span class="material-symbols-outlined icon">{link['icono']}</span>

            <div class="title" style="color:{link['color']}">
                {link['titulo']}
            </div>

            <div class="desc">{link['descripcion']}</div>

            <div class="number">{link['numero']}</div>

        </div>

    </div>

    """


html = f"""

<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">

<style>

body {{
font-family: sans-serif;
}}

.card {{
    border-radius:12px;
    padding:18px;
    margin-bottom:16px;
    border:1px solid #ddd;
    background:#f9f9fb;
    cursor:pointer;
    transition:0.2s;
}}

.card:hover {{
    background:#eef2ff;
    transform:scale(1.01);
}}

.grid {{
    display:grid;
    grid-template-columns:60px 1fr auto;
    grid-template-rows:auto auto;
    gap:6px;
    align-items:center;
}}

.icon {{
    grid-column:1;
    grid-row:1 / span 2;
    display:flex;
    align-items:center;
    justify-content:center;
}}

.title {{
    grid-column:2;
    grid-row:1;
    font-weight:600;
    font-size:16px;
}}

.desc {{
    grid-column:2;
    grid-row:2;
    font-size:14px;
    color:#444;
}}

.number {{
    grid-column:3;
    grid-row:1;
    font-weight:bold;
    color:#777;
}}

.material-symbols-outlined {{
    font-size:34px;
}}

</style>

{cards_html}

"""

components.html(html, height=400, scrolling=True)