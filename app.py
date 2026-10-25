"""Observatorio de Turismo Sostenible — Guatemala.

Tablero interactivo del Laboratorio 10 (Visualización Interactiva, CC3066 Data Science).
Reutiliza datos y modelos de pronóstico del Laboratorio 2.

Ejecutar con:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from dashboard import theme as T
from dashboard.views import inicio, explorar, modelos, perfil

st.set_page_config(
    page_title="Observatorio de Turismo · Guatemala",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(T.APP_CSS, unsafe_allow_html=True)

pages = [
    st.Page(inicio.render, title="Inicio", icon="🏠", url_path="inicio", default=True),
    st.Page(explorar.render, title="Explorar los datos", icon="🔎", url_path="explorar"),
    st.Page(modelos.render, title="Modelos y pronósticos", icon="📈", url_path="modelos"),
    st.Page(perfil.render, title="Perfil de series", icon="🧭", url_path="perfil"),
]

with st.sidebar:
    st.markdown("### 🌋 Observatorio de Turismo")
    st.caption("Guatemala · 2009–2026")
    st.markdown(
        "<small>Tablero para directivos del sector turístico. "
        "Datos: ingreso de visitantes no residentes (INGUAT / migración).</small>",
        unsafe_allow_html=True,
    )

nav = st.navigation(pages)
nav.run()

with st.sidebar:
    st.divider()
    st.caption(
        "Laboratorio 10 · CC3066 Data Science · UVG. "
        "Modelos reutilizados del Laboratorio 2 (redes LSTM)."
    )
