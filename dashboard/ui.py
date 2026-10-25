"""Utilidades compartidas de la interfaz: datos cacheados y componentes comunes."""

from __future__ import annotations

import streamlit as st

from . import loaders as L
from . import theme as T


# ---------------------------------------------------------------------------
# Datos cacheados (se leen una sola vez por sesión)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Cargando datos de visitantes…")
def series_long():
    return L.load_series_long()


@st.cache_data(show_spinner=False)
def breakdown(dimension: str):
    return L.load_breakdown(dimension)


@st.cache_data(show_spinner=False)
def country_breakdown(top_n: int = 12):
    return L.load_country_breakdown(top_n)


@st.cache_data(show_spinner=False)
def predictions():
    return L.load_predictions()


@st.cache_data(show_spinner=False)
def metrics():
    return L.load_metrics()


@st.cache_data(show_spinner=False)
def tuning_trials():
    return L.load_tuning_trials()


@st.cache_data(show_spinner=False)
def catch22_pca():
    return L.load_catch22_pca()


@st.cache_data(show_spinner=False)
def catch22_distance():
    return L.load_catch22_distance()


@st.cache_data(show_spinner=False)
def catch22_variance():
    return L.catch22_pca_variance()


# ---------------------------------------------------------------------------
# Componentes visuales reutilizables
# ---------------------------------------------------------------------------
def hero(title: str, subtitle: str):
    st.markdown(
        f"""<div class="app-hero"><h1>{title}</h1><p>{subtitle}</p></div>""",
        unsafe_allow_html=True,
    )


def note(text: str):
    st.markdown(f'<div class="note">{text}</div>', unsafe_allow_html=True)


def empty(text: str):
    st.markdown(f'<div class="empty">⚠️ {text}</div>', unsafe_allow_html=True)


def plotly(fig, **kwargs):
    """Muestra una figura Plotly con estilo y configuración coherentes."""
    config = {"displayModeBar": False, "displaylogo": False}
    return st.plotly_chart(fig, use_container_width=True, config=config, **kwargs)


def clicked_category(event):
    """Devuelve la categoría de texto del primer punto seleccionado, o None.

    Funciona para barras verticales (categoría en x) y horizontales (en y):
    toma el primer valor que sea texto.
    """
    try:
        pts = event["selection"]["points"]
    except (TypeError, KeyError):
        return None
    if not pts:
        return None
    p = pts[0]
    for key in ("label", "x", "y"):
        v = p.get(key)
        if isinstance(v, str):
            return v
    cd = p.get("customdata")
    if cd:
        return cd[0] if isinstance(cd, (list, tuple)) else cd
    return None
