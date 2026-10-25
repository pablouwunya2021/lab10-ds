"""Página de inicio: contexto, alcance y lectura rápida del observatorio."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .. import theme as T
from .. import ui


def render():
    ui.hero(
        "Observatorio de Turismo Sostenible · Guatemala",
        "Ingreso de visitantes no residentes (turistas y excursionistas), 2009–2026. "
        "Explore los datos, compare pronósticos y consulte sus limitaciones.",
    )

    df = ui.series_long()
    total = df[df["serie_key"] == "total"].sort_values("fecha")

    # --- Tarjetas de lectura rápida (elementos complementarios) ------------
    last12 = total.tail(12)["valor"].sum()
    prev12 = total.tail(24).head(12)["valor"].sum()
    yoy = (last12 / prev12 - 1) * 100 if prev12 else 0.0
    # Recuperación frente al mismo tramo pre-pandemia (jul 2018 – jun 2019).
    pre = total[(total["fecha"] >= "2018-07-01") & (total["fecha"] <= "2019-06-01")]["valor"].sum()
    recup = (last12 / pre * 100) if pre else 0.0
    peak_month = total.loc[total["valor"].idxmax()]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Visitantes · últimos 12 meses", T.fmt_compact(last12),
              help=f"{T.fmt_int(last12)} visitantes")
    c2.metric("Variación interanual", T.fmt_pct(yoy), delta=T.fmt_pct(yoy))
    c3.metric("Recuperación vs. 2018–2019", T.fmt_pct(recup))
    c4.metric("Mes pico histórico", peak_month["fecha"].strftime("%b %Y").capitalize(),
              help=f"{T.fmt_int(peak_month['valor'])} visitantes")

    ui.note(
        "Las tarjetas resumen el dato más reciente. El período de prueba de los modelos "
        "(abril 2021 – junio 2026) incluye la caída por la pandemia de COVID-19 y la "
        "recuperación posterior, por eso los errores de pronóstico son altos: es un contexto "
        "atípico, no un fallo de los datos."
    )

    # --- Panorama general --------------------------------------------------
    st.subheader("Panorama: total mensual de visitantes")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=total["fecha"], y=total["valor"], mode="lines",
            line=dict(color=T.BRAND, width=2),
            fill="tozeroy", fillcolor="rgba(15,118,110,0.08)",
            name="Total", hovertemplate="%{x|%b %Y}<br>%{y:,.0f} visitantes<extra></extra>",
        )
    )
    fig.add_vrect(
        x0=pd.Timestamp("2021-04-01"), x1=total["fecha"].max(),
        fillcolor="rgba(43,166,164,0.06)", line_width=0,
        annotation_text="Ventana de prueba de modelos", annotation_position="top left",
        annotation_font_size=11,
    )
    fig.update_layout(**T.base_layout(height=330, legend=False))
    ui.plotly(fig)

    cols = st.columns(3)
    with cols[0]:
        st.markdown("#### ¿Qué puede hacer aquí?")
        st.markdown(
            "- **Explorar los datos**: tendencias, estacionalidad y composición por vía "
            "de ingreso y región de origen.\n"
            "- **Modelos y pronósticos**: comparar 3 modelos y ver qué tan bien predicen.\n"
            "- **Perfil de series**: en qué se parecen y se diferencian las series."
        )
    with cols[1]:
        st.markdown("#### Para quién")
        st.markdown(
            "Directivos y tomadores de decisiones del sector turístico. No se requiere "
            "formación estadística: cada vista incluye textos que explican qué muestra y "
            "para qué sirve."
        )
    with cols[2]:
        st.markdown("#### Cómo leer los colores")
        st.markdown(
            f"- <span style='color:{T.COLORS_VIA['Aérea']};font-weight:600'>Aérea</span>, "
            f"<span style='color:{T.COLORS_VIA['Terrestre']};font-weight:600'>Terrestre</span>, "
            f"<span style='color:{T.COLORS_VIA['Marítima']};font-weight:600'>Marítima</span>: "
            "vía de ingreso.\n"
            f"- <span style='color:{T.COLOR_OBSERVADO};font-weight:600'>Gris</span>: dato "
            "observado. Colores vivos: estimaciones de los modelos.",
            unsafe_allow_html=True,
        )
