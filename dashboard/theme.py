"""Paleta de colores, tipografía y plantilla de gráficos del tablero.

La paleta se basa en la teoría del color vista en clase:

- Un color de marca (turquesa) que evoca los lagos y costas de Guatemala y
  mantiene coherencia visual en toda la aplicación.
- Colores CATEGÓRICOS con significado FIJO: cada vía de ingreso, cada región y
  cada modelo conservan su color en todas las vistas, para que el usuario los
  reconozca sin releer leyendas.
- Una escala SECUENCIAL (un solo tono que oscurece con la magnitud) para mapas
  de calor, porque representan "más vs. menos".
- Una escala DIVERGENTE (dos tonos con centro neutro) solo para el error de
  pronóstico, donde el signo importa (sobrestima vs. subestima).

Los colores se eligieron buscando contraste suficiente (texto AA) y que sean
distinguibles también para daltonismo rojo-verde.
"""

from __future__ import annotations

# --- Marca y neutros -------------------------------------------------------
BRAND = "#0F766E"          # turquesa profundo (color principal)
BRAND_SOFT = "#14B8A6"     # turquesa claro (acentos / hover)
INK = "#1F2A33"            # texto principal
MUTED = "#5B6B76"          # texto secundario
GRID = "#E3E9ED"           # líneas de rejilla
SURFACE = "#FFFFFF"        # fondo de tarjetas
CANVAS = "#F6F8F9"         # fondo de la app

OK = "#2E7D5B"             # positivo / buen desempeño
WARN = "#C2672B"           # atención
BAD = "#B23A48"            # alto error / negativo

# --- Vías de ingreso (significado fijo) ------------------------------------
COLORS_VIA = {
    "Aérea": "#1B6FB3",       # azul cielo
    "Terrestre": "#E08A1E",   # ámbar (carretera / tierra)
    "Marítima": "#2BA6A4",    # turquesa (mar)
}

# --- Regiones de origen (significado fijo) ---------------------------------
COLORS_REGION = {
    "América Del Centro": "#2BA6A4",
    "América Del Norte": "#1B6FB3",
    "Europa": "#7A4FA3",
    "América Del Sur y el Caribe": "#E08A1E",
    "Asia": "#C2425B",
    "Oceanía": "#5B8C3E",
    "Oriente Medio": "#B07B3E",
    "Otros Paises Del Mundo": "#8A99A5",
}

# --- Modelos (significado fijo) --------------------------------------------
COLOR_OBSERVADO = "#2F3B44"   # gris oscuro, serie real
COLORS_MODELO = {
    "LSTM simple": "#1B6FB3",
    "LSTM apilado": "#E08A1E",
    "LSTM global (catch22)": "#2BA6A4",
}

# --- Escalas continuas -----------------------------------------------------
# Secuencial (magnitudes): de claro a turquesa oscuro.
SEQ_TEAL = [
    [0.0, "#EAF4F3"],
    [0.25, "#ABDAD6"],
    [0.5, "#5FBDB7"],
    [0.75, "#1E938C"],
    [1.0, "#0B5E59"],
]

# Divergente (error con signo): azul (sobrestima) ↔ rojo (subestima).
DIV_ERROR = [
    [0.0, "#1B6FB3"],
    [0.5, "#F2F4F5"],
    [1.0, "#B23A48"],
]

CLUSTER_COLORS = {1: "#7A4FA3", 2: "#1B6FB3", 3: "#E08A1E", 4: "#2E7D5B"}

FONT_FAMILY = (
    "Inter, 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
)


def base_layout(height: int = 360, legend: bool = True) -> dict:
    """Diccionario de layout común para todas las figuras Plotly."""
    return dict(
        template="plotly_white",
        height=height,
        font=dict(family=FONT_FAMILY, size=13, color=INK),
        title=dict(font=dict(size=16, color=INK)),
        margin=dict(l=55, r=20, t=50, b=45),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=12),
        )
        if legend
        else dict(visible=False),
        hoverlabel=dict(font=dict(family=FONT_FAMILY, size=12)),
    )


def fmt_int(value: float) -> str:
    """Formatea un entero con separador de miles (estilo es-GT: punto)."""
    try:
        return f"{int(round(value)):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "—"


def fmt_compact(value: float) -> str:
    """Formato compacto para tarjetas: 3,33 M / 845,2 k."""
    try:
        v = float(value)
    except (ValueError, TypeError):
        return "—"
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:.2f} M".replace(".", ",")
    if abs(v) >= 1_000:
        return f"{v/1_000:.1f} k".replace(".", ",")
    return f"{int(round(v))}"


def fmt_pct(value: float, decimals: int = 1) -> str:
    try:
        return f"{value:.{decimals}f}%".replace(".", ",")
    except (ValueError, TypeError):
        return "—"


# CSS global de la aplicación (tipografía, tarjetas, encabezados).
APP_CSS = f"""
<style>
    html, body, [class*="css"] {{ font-family: {FONT_FAMILY}; }}
    .main .block-container {{ padding-top: 1.4rem; max-width: 1200px; }}
    h1, h2, h3 {{ color: {INK}; font-weight: 700; letter-spacing: -0.01em; }}
    .app-hero {{
        background: linear-gradient(100deg, {BRAND} 0%, {BRAND_SOFT} 100%);
        color: white; padding: 1.1rem 1.4rem; border-radius: 14px;
        margin-bottom: 1.0rem;
    }}
    .app-hero h1 {{ color: white; margin: 0; font-size: 1.5rem; }}
    .app-hero p {{ color: rgba(255,255,255,0.92); margin: 0.25rem 0 0 0; font-size: 0.95rem; }}
    .note {{
        background: #EAF4F3; border-left: 4px solid {BRAND};
        padding: 0.7rem 0.95rem; border-radius: 8px; color: {INK};
        font-size: 0.9rem; margin: 0.4rem 0 0.9rem 0;
    }}
    .empty {{
        background: #FFF4E6; border-left: 4px solid {WARN};
        padding: 0.7rem 0.95rem; border-radius: 8px; color: {INK};
        font-size: 0.9rem;
    }}
    div[data-testid="stMetric"] {{
        background: {SURFACE}; border: 1px solid {GRID};
        border-radius: 12px; padding: 0.7rem 0.9rem;
    }}
    div[data-testid="stMetricLabel"] p {{ color: {MUTED}; font-size: 0.8rem; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.5rem; }}
</style>
"""
