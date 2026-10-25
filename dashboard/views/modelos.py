"""Modelos y pronósticos: comparación de 3 modelos y desempeño enlazado."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from .. import theme as T
from .. import ui

METRIC_INFO = {
    "mae": ("MAE", "Error promedio en número de visitantes. Más bajo es mejor."),
    "rmse": ("RMSE", "Como el MAE pero penaliza más los errores grandes. Más bajo es mejor."),
    "mape": ("MAPE", "Error promedio en porcentaje. Más bajo es mejor."),
    "mase": ("MASE", "Compara contra un pronóstico ingenuo estacional; < 1 significa que le gana."),
}


def render():
    st.title("Modelos y pronósticos")
    st.caption(
        "Resultados de tres modelos de pronóstico (redes LSTM) reutilizados del Laboratorio 2. "
        "Aquí no se entrenan modelos nuevos: se comparan sus predicciones sobre datos que no vieron."
    )

    preds = ui.predictions()
    mets = ui.metrics()

    serie_opts = preds[["serie_key", "serie"]].drop_duplicates().set_index("serie")["serie_key"].to_dict()
    c1, c2 = st.columns([2, 2])
    with c1:
        serie_label = st.selectbox("Serie a pronosticar", list(serie_opts.keys()), index=0)
    with c2:
        metric = st.selectbox(
            "Métrica para comparar", list(METRIC_INFO.keys()),
            format_func=lambda m: f"{METRIC_INFO[m][0]} — {METRIC_INFO[m][1].split('.')[0]}",
        )
    serie_key = serie_opts[serie_label]

    sp = preds[preds["serie_key"] == serie_key]
    sm = mets[mets["serie_key"] == serie_key].copy()
    modelos = list(sm.sort_values(metric)["modelo"])

    state_key = f"modelo_sel_{serie_key}"
    if state_key not in st.session_state or st.session_state[state_key] not in modelos:
        st.session_state[state_key] = modelos[0]  # mejor en la métrica actual

    ui.note(
        f"<b>{METRIC_INFO[metric][0]}:</b> {METRIC_INFO[metric][1]} "
        "Elija el modelo en el menú <b>«Modelo resaltado»</b> (o haga clic en un punto del gráfico) "
        "y se resaltará en el pronóstico, el error y la búsqueda de hiperparámetros."
    )

    left, right = st.columns([1, 1.4])

    # ------------------------------------------------ VIZ 7 (B1): comparación
    with left:
        st.subheader("Comparación de modelos")
        sel = st.session_state[state_key]
        order = list(sm.sort_values(metric, ascending=False)["modelo"])  # mayor arriba→abajo
        smo = sm.set_index("modelo").loc[order].reset_index()
        figc = go.Figure()
        # Tallos (lollipop) — no capturan clics.
        for _, r in smo.iterrows():
            base = T.COLORS_MODELO.get(r["modelo"], T.BRAND)
            figc.add_shape(
                type="line", x0=0, x1=r[metric], y0=r["modelo"], y1=r["modelo"],
                line=dict(color=base if r["modelo"] == sel else _fade(base), width=3),
            )
        # Marcadores clicables.
        figc.add_trace(
            go.Scatter(
                x=smo[metric], y=smo["modelo"], mode="markers+text",
                text=[_fmt_metric(metric, v) for v in smo[metric]], textposition="middle right",
                marker=dict(
                    size=20,
                    color=[T.COLORS_MODELO.get(m, T.BRAND) if m == sel
                           else _fade(T.COLORS_MODELO.get(m, T.BRAND)) for m in smo["modelo"]],
                    line=dict(width=2, color="white"),
                ),
                customdata=smo["modelo"],
                hovertemplate="%{y}<br>" + METRIC_INFO[metric][0] + ": %{x:,.1f}<extra></extra>",
                cliponaxis=False,
            )
        )
        figc.update_layout(**T.base_layout(height=300, legend=False))
        figc.update_xaxes(title=METRIC_INFO[metric][0], rangemode="tozero")
        figc.update_layout(margin=dict(l=130, r=70, t=20, b=45), clickmode="event+select", dragmode="select")
        ev = ui.plotly(figc, on_select="rerun", key=f"cmp_{serie_key}")
        clicked = ui.clicked_category(ev)
        if clicked and clicked in modelos and clicked != st.session_state[state_key]:
            st.session_state[state_key] = clicked
            st.rerun()
        sel2 = st.selectbox(
            "Modelo resaltado", modelos, index=modelos.index(st.session_state[state_key]),
            key=f"selmod_{serie_key}",
        )
        if sel2 != st.session_state[state_key]:
            st.session_state[state_key] = sel2
            st.rerun()

    sel = st.session_state[state_key]

    # --------------------------------------- VIZ 6 (B2): pronóstico vs observado
    with right:
        st.subheader("Pronóstico vs. observado")
        obs = sp[sp["modelo"] == modelos[0]].sort_values("fecha")
        figf = go.Figure()
        figf.add_trace(
            go.Scatter(
                x=obs["fecha"], y=obs["observado"], name="Observado",
                mode="lines", line=dict(color=T.COLOR_OBSERVADO, width=3),
                hovertemplate="%{x|%b %Y}<br>Observado: %{y:,.0f}<extra></extra>",
            )
        )
        for m in modelos:
            d = sp[sp["modelo"] == m].sort_values("fecha")
            highlight = m == sel
            figf.add_trace(
                go.Scatter(
                    x=d["fecha"], y=d["predicho"], name=m, mode="lines",
                    line=dict(
                        color=T.COLORS_MODELO.get(m, T.BRAND),
                        width=3 if highlight else 1.3,
                        dash="solid" if highlight else "dot",
                    ),
                    opacity=1.0 if highlight else 0.6,
                    hovertemplate="%{x|%b %Y}<br>" + m + ": %{y:,.0f}<extra></extra>",
                )
            )
        figf.update_layout(**T.base_layout(height=330), yaxis_title="Visitantes")
        ui.plotly(figf)

    # ------------------------------------------- VIZ 8 (B3): error en el tiempo
    st.divider()
    cL, cR = st.columns([1.4, 1])
    with cL:
        st.subheader(f"Error de pronóstico en el tiempo · {sel}")
        d = sp[sp["modelo"] == sel].sort_values("fecha")
        bar_colors = [T.COLORS_MODELO.get(sel, T.BRAND) if e >= 0 else T.BAD for e in d["error"]]
        fige = go.Figure(
            go.Bar(
                x=d["fecha"], y=d["error"], marker_color=bar_colors,
                hovertemplate="%{x|%b %Y}<br>Error: %{y:,.0f}<extra></extra>",
            )
        )
        fige.add_hline(y=0, line_color=T.MUTED, line_width=1)
        fige.update_layout(**T.base_layout(height=300, legend=False), yaxis_title="Observado − Predicho")
        ui.plotly(fige)
        ui.note(
            "Barras sobre cero: el modelo <b>subestimó</b> (llegaron más visitantes de los previstos). "
            "Bajo cero: <b>sobrestimó</b>. Ayuda a ver en qué meses falla más."
        )

    # --------------------------------------- VIZ 9: búsqueda de hiperparámetros
    with cR:
        st.subheader("Búsqueda de hiperparámetros")
        trials = ui.tuning_trials()
        tt = trials[(trials["serie_key"] == serie_key) & (trials["modelo"] == sel)].copy()
        if tt.empty:
            ui.empty(
                "Este modelo (global catch22) no se obtuvo por búsqueda individual de "
                "hiperparámetros, por eso no tiene curva de ensayos."
            )
        else:
            tt = tt.sort_values("val_loss").reset_index(drop=True)
            tt["ensayo"] = tt.index + 1
            figt = go.Figure(
                go.Scatter(
                    x=tt["ensayo"], y=tt["val_loss"], mode="lines+markers",
                    line=dict(color=T.COLORS_MODELO.get(sel, T.BRAND), width=2),
                    marker=dict(size=7),
                    hovertemplate="Ensayo %{x}<br>val_loss: %{y:.4f}<extra></extra>",
                )
            )
            figt.update_layout(**T.base_layout(height=300, legend=False))
            figt.update_xaxes(title="Ensayos (ordenados de mejor a peor)")
            figt.update_yaxes(title="Pérdida de validación")
            ui.plotly(figt)
            ui.note(
                "Cada punto es una combinación de hiperparámetros probada. Se eligió la de "
                "menor pérdida de validación (extremo izquierdo)."
            )

    # ------------------------------------------- Tabla comparativa (complemento)
    st.divider()
    st.subheader("Tabla comparativa de modelos")
    show = sm[["modelo", "mae", "rmse", "mape", "mase"]].sort_values(metric).reset_index(drop=True)
    show.columns = ["Modelo", "MAE", "RMSE", "MAPE (%)", "MASE"]
    st.dataframe(
        show.style.format({"MAE": "{:,.0f}", "RMSE": "{:,.0f}", "MAPE (%)": "{:.1f}", "MASE": "{:.2f}"})
        .highlight_min(subset=["MAE", "RMSE", "MAPE (%)", "MASE"], color="#D9F0EC"),
        use_container_width=True, hide_index=True,
    )
    ui.note(
        "El mejor valor de cada métrica aparece resaltado. <b>Limitación:</b> todos los MASE "
        "son mayores que 1, es decir, en esta ventana atípica (pandemia y recuperación) los "
        "modelos no superan a un pronóstico estacional ingenuo. Úselos como referencia de "
        "tendencia, no como cifras exactas de planificación."
    )


def _fmt_metric(metric: str, v: float) -> str:
    if metric == "mape":
        return f"{v:.1f}%"
    if metric == "mase":
        return f"{v:.2f}"
    return f"{v:,.0f}"


def _fade(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},0.35)"
