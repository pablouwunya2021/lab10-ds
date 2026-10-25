"""Perfil de series: en qué se parecen y se diferencian las series (análisis catch22)."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from .. import theme as T
from .. import ui


def render():
    st.title("Perfil de las series")
    st.caption(
        "¿Qué series de visitantes se comportan parecido? Este análisis resume cada serie con "
        "22 características (tendencia, estacionalidad, variabilidad, etc.) y las compara entre sí."
    )
    ui.note(
        "Se usó <b>catch22</b>, un conjunto estándar de 22 indicadores que describen la «forma» "
        "de una serie de tiempo. No requiere interpretarlos uno por uno: lo relevante es que "
        "<b>series cercanas se comportan de manera similar</b> y podrían gestionarse con criterios parecidos."
    )

    pca = ui.catch22_pca()
    var = ui.catch22_variance()

    c1, c2 = st.columns([1.3, 1])

    # --------------------------------------------------- VIZ 10: PCA scatter
    with c1:
        st.subheader("Mapa de similitud entre series")
        fig = go.Figure()
        for cl in sorted(pca["cluster"].unique()):
            d = pca[pca["cluster"] == cl]
            fig.add_trace(
                go.Scatter(
                    x=d["PC1"], y=d["PC2"], mode="markers+text",
                    text=d["serie"], textposition="top center",
                    name=f"Grupo {cl}",
                    marker=dict(size=16, color=T.CLUSTER_COLORS.get(int(cl), T.BRAND),
                                line=dict(width=1, color="white")),
                    hovertemplate="%{text}<extra></extra>",
                )
            )
        fig.update_layout(**T.base_layout(height=430))
        fig.update_xaxes(title=f"Componente 1 ({var[0]*100:.0f}% de la variación)")
        fig.update_yaxes(title=f"Componente 2 ({var[1]*100:.0f}% de la variación)")
        ui.plotly(fig)
        ui.note(
            "Cada punto es una serie; los colores son grupos de comportamiento similar. "
            "Dos series próximas comparten patrón (por ejemplo, estacionalidad y recuperación "
            "parecidas). La <b>vía marítima</b> aparece aislada: su dinámica es muy distinta."
        )

    # ------------------------------------------------ VIZ 11: distancia (heatmap)
    with c2:
        st.subheader("Distancia entre series")
        dist = ui.catch22_distance()
        fig2 = go.Figure(
            go.Heatmap(
                z=dist.values, x=list(dist.columns), y=list(dist.index),
                colorscale=T.SEQ_TEAL, reversescale=True,
                colorbar=dict(title="Distancia"),
                hovertemplate="%{y} ↔ %{x}<br>Distancia: %{z:.2f}<extra></extra>",
            )
        )
        fig2.update_layout(**T.base_layout(height=430, legend=False))
        fig2.update_xaxes(tickangle=-40)
        ui.plotly(fig2)
        ui.note(
            "Más oscuro = más parecidas. La diagonal es cero (cada serie consigo misma)."
        )

    st.divider()
    st.markdown(
        "#### ¿Para qué sirve esto a un directivo?\n"
        "Si dos mercados o vías de ingreso se comportan igual, una misma estrategia "
        "(promoción, capacidad, pronóstico) puede aplicarse a ambos. Un segmento que aparece "
        "aislado —como la vía marítima— exige un tratamiento aparte y pronósticos propios."
    )
