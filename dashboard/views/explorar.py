"""Exploración de los datos: tendencia, estacionalidad, composición y detalle enlazado."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from .. import theme as T
from .. import ui
from ..loaders import MONTH_NAMES_ES


def render():
    st.title("Explorar los datos")
    st.caption(
        "Observe por sí mismo las tendencias de ingreso de visitantes. Use los controles "
        "para elegir la serie, el nivel de detalle y el período."
    )

    df = ui.series_long()
    series_opts = (
        df[["serie_key", "serie"]].drop_duplicates().set_index("serie")["serie_key"].to_dict()
    )

    ctl1, ctl2, ctl3 = st.columns([2, 1.3, 2])
    with ctl1:
        serie_label = st.selectbox("Serie a explorar", list(series_opts.keys()), index=0)
    with ctl2:
        granularidad = st.radio(
            "Nivel de detalle", ["Mensual", "Anual"], horizontal=True,
            help="Cambie entre el detalle mes a mes y el resumen anual.",
        )
    with ctl3:
        years = sorted(df["anio"].unique())
        rango = st.select_slider(
            "Período (años)", options=years, value=(years[0], years[-1]),
        )

    serie_key = series_opts[serie_label]
    s = df[(df["serie_key"] == serie_key) & df["anio"].between(*rango)].sort_values("fecha")

    if s["valor"].sum() == 0:
        ui.empty("La selección no tiene visitantes registrados en este período.")
        return

    # ---------------------------------------------------------------- VIZ 1
    st.subheader(f"1 · Evolución de «{serie_label}»")
    if granularidad == "Mensual":
        fig1 = go.Figure(
            go.Scatter(
                x=s["fecha"], y=s["valor"], mode="lines",
                line=dict(color=T.BRAND, width=2),
                hovertemplate="%{x|%b %Y}<br>%{y:,.0f}<extra></extra>",
            )
        )
        fig1.update_xaxes(rangeslider=dict(visible=True), rangeslider_thickness=0.08)
        sub = "Arrastre la barra inferior para acercar un período concreto."
    else:
        anual = s.groupby("anio")["valor"].sum().reset_index()
        fig1 = go.Figure(
            go.Bar(
                x=anual["anio"], y=anual["valor"], marker_color=T.BRAND,
                hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>",
            )
        )
        sub = "Totales por año. Cambie a «Mensual» para ver el detalle dentro de cada año."
    fig1.update_layout(**T.base_layout(height=340, legend=False), yaxis_title="Visitantes")
    ui.plotly(fig1)
    ui.note(f"{sub} Útil para ver si el destino crece, se estanca o se recupera.")

    # ---------------------------------------------------------------- VIZ 2
    st.subheader("2 · Estacionalidad: ¿en qué meses llegan más visitantes?")
    pivot = (
        s.pivot_table(index="anio", columns="mes", values="valor", aggfunc="sum")
        .reindex(columns=range(1, 13))
    )
    fig2 = go.Figure(
        go.Heatmap(
            z=pivot.values, x=[MONTH_NAMES_ES[m - 1] for m in pivot.columns],
            y=pivot.index, colorscale=T.SEQ_TEAL,
            colorbar=dict(title="Visitantes"),
            hovertemplate="%{y} · %{x}<br>%{z:,.0f}<extra></extra>",
        )
    )
    fig2.update_layout(**T.base_layout(height=max(260, 24 * len(pivot) + 120), legend=False))
    fig2.update_yaxes(autorange="reversed", type="category")
    ui.plotly(fig2)
    ui.note(
        "Cada celda es un mes. Los tonos más oscuros marcan la temporada alta; sirve para "
        "planear capacidad hotelera, personal y campañas según el calendario."
    )

    st.divider()

    # ----------------------------------------------- VIZ 3: composición por vía
    st.subheader("3 · Composición por vía de ingreso")
    vias = ui.breakdown("Vía")
    vias = vias[vias["anio"].between(*rango)]
    if granularidad == "Anual":
        vcomp = vias.groupby(["anio", "categoria"])["valor"].sum().reset_index()
        xcol = "anio"
    else:
        vcomp = vias.groupby(["fecha", "categoria"])["valor"].sum().reset_index()
        xcol = "fecha"
    fig3 = go.Figure()
    for via in ["Aérea", "Terrestre", "Marítima"]:
        d = vcomp[vcomp["categoria"] == via]
        fig3.add_trace(
            go.Scatter(
                x=d[xcol], y=d["valor"], name=via, mode="lines",
                stackgroup="one", line=dict(width=0.5, color=T.COLORS_VIA[via]),
                fillcolor=T.COLORS_VIA[via],
                hovertemplate="%{x}<br>" + via + ": %{y:,.0f}<extra></extra>",
            )
        )
    fig3.update_layout(**T.base_layout(height=330), yaxis_title="Visitantes")
    ui.plotly(fig3)
    ui.note(
        "Área apilada: muestra cuánto aporta cada vía al total y cómo cambia su peso en el "
        "tiempo. Haga clic en la leyenda para aislar una vía."
    )

    st.divider()

    # ------------------------------ VIZ 4 + 5: par ENLAZADO (origen → detalle)
    st.subheader("4 · Origen de los visitantes  →  5 · Detalle en el tiempo")
    st.caption(
        "Gráficos enlazados: elija un origen en el menú **«O elija del menú»** (o haga clic en "
        "una barra) y la serie de la derecha se actualiza para mostrar su evolución; además la "
        "barra seleccionada se resalta en el ranking."
    )

    nivel = st.radio(
        "Ver origen por", ["Región", "País"], horizontal=True,
        help="Aumente el detalle pasando de grandes regiones a países individuales.",
    )

    if nivel == "Región":
        bd = ui.breakdown("Región dos")
        catcol = "categoria"
        color_map = T.COLORS_REGION
    else:
        bd = ui.country_breakdown()
        catcol = "pais"
        color_map = None
    bd = bd[bd["anio"].between(*rango)]

    totals = (
        bd.groupby(catcol)["valor"].sum().sort_values(ascending=False).reset_index()
    )
    cats = list(totals[catcol])
    if not cats:
        ui.empty("No hay datos de origen para el período seleccionado.")
        return

    state_key = f"origen_sel_{nivel}"
    if state_key not in st.session_state or st.session_state[state_key] not in cats:
        st.session_state[state_key] = cats[0]

    left, right = st.columns([1.05, 1.25])

    with left:
        colors = [color_map.get(c, T.MUTED) for c in cats] if color_map else None
        bar_colors = []
        for c in cats:
            base = (color_map.get(c, T.BRAND) if color_map else T.BRAND)
            bar_colors.append(base if c == st.session_state[state_key] else _fade(base))
        figb = go.Figure(
            go.Bar(
                x=totals["valor"], y=totals[catcol], orientation="h",
                marker_color=bar_colors,
                hovertemplate="%{y}<br>%{x:,.0f} visitantes<extra></extra>",
            )
        )
        figb.update_layout(**T.base_layout(height=max(300, 30 * len(cats) + 120), legend=False))
        figb.update_yaxes(autorange="reversed")
        figb.update_xaxes(title="Visitantes acumulados en el período")
        ev = ui.plotly(figb, on_select="rerun", key=f"bar_{nivel}")
        clicked = ui.clicked_category(ev)
        if clicked and clicked in cats and clicked != st.session_state[state_key]:
            st.session_state[state_key] = clicked
            st.rerun()
        # Control alterno (accesible), sincronizado con el clic.
        sel = st.selectbox(
            "O elija del menú", cats, index=cats.index(st.session_state[state_key]),
            key=f"sel_{nivel}",
        )
        if sel != st.session_state[state_key]:
            st.session_state[state_key] = sel
            st.rerun()

    sel = st.session_state[state_key]
    with right:
        d = bd[bd[catcol] == sel].groupby("fecha")["valor"].sum().reset_index()
        line_color = (color_map.get(sel, T.BRAND) if color_map else T.BRAND)
        figd = go.Figure(
            go.Scatter(
                x=d["fecha"], y=d["valor"], mode="lines",
                line=dict(color=line_color, width=2.2),
                fill="tozeroy", fillcolor=_rgba(line_color, 0.08),
                hovertemplate="%{x|%b %Y}<br>%{y:,.0f}<extra></extra>",
            )
        )
        figd.update_layout(
            **T.base_layout(height=max(300, 30 * len(cats) + 120), legend=False),
            yaxis_title="Visitantes",
        )
        figd.update_layout(title=dict(text=f"Evolución mensual · {sel}",
                                      font=dict(size=15, color=T.INK)))
        ui.plotly(figd)

    share = totals.loc[totals[catcol] == sel, "valor"].iloc[0] / totals["valor"].sum() * 100
    ui.note(
        f"<b>{sel}</b> representa el <b>{T.fmt_pct(share)}</b> de los visitantes del período "
        "seleccionado. Cambie «Ver origen por» entre Región y País para aumentar o disminuir "
        "el nivel de detalle."
    )


def _fade(hex_color: str) -> str:
    return _rgba(hex_color, 0.35)


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
