"""Carga y preparación de datos para el tablero.

Reutiliza íntegramente las definiciones del Laboratorio 1/2 (`lstm_lab2.data`)
para reconstruir las series mensuales de visitantes a Guatemala y para cargar las
predicciones y métricas de los modelos LSTM ya entrenados en el Laboratorio 2.

No se entrena ningún modelo nuevo: aquí solo se *leen* los resultados guardados en
`Lab2DS/outputs/`.
"""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

# --- Rutas al proyecto del Laboratorio 2 -----------------------------------
ROOT = Path(__file__).resolve().parent.parent
LAB2 = ROOT / "Lab2DS"
OUTPUTS = LAB2 / "outputs"
DATA_FILE = LAB2 / "Base_Migracion_2009-2026jun.xlsx"

if str(LAB2) not in sys.path:
    sys.path.insert(0, str(LAB2))

from lstm_lab2 import data as lab2_data  # noqa: E402  (requiere LAB2 en sys.path)

# Ventana de prueba (misma partición 70/30 del Laboratorio 1).
TEST_START = lab2_data.TEST_START
TEST_END = lab2_data.TEST_END
TRAIN_END = lab2_data.TRAIN_END

# Claves de serie y etiqueta legible.
SERIES_KEYS = [
    "total",
    "air_entry",
    "land_entry",
    "sea_entry",
    "central_america",
    "north_america",
    "europe",
]

# Agrupación de las series por tema, para la navegación.
SERIES_BY_THEME = {
    "Vía de ingreso": ["air_entry", "land_entry", "sea_entry"],
    "Región de origen": ["central_america", "north_america", "europe"],
    "Agregado": ["total"],
}

MONTH_NAMES_ES = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]


# ---------------------------------------------------------------------------
# Lectura única del Excel (cacheada): evita releer 161k filas en cada serie.
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _raw() -> pd.DataFrame:
    """Lee el Excel una sola vez y agrega la columna de fecha."""
    return lab2_data._load_raw()


def _series_from_raw(raw: pd.DataFrame, key: str) -> pd.Series:
    """Construye una serie mensual a partir del Excel ya leído (misma lógica de data.py)."""
    if key == "sea_entry":
        column, value = lab2_data.SEA_ENTRY_FILTER
        subset = raw[raw[column] == value]
    else:
        subset = lab2_data._reference_population(raw)
        entry_filter = lab2_data.SERIES_DEFINITIONS[key]["filter"]
        if entry_filter is not None:
            column, value = entry_filter
            subset = subset[subset[column] == value]
    series = subset.groupby("date")["Viajero"].sum().sort_index().asfreq("MS", fill_value=0.0)
    series.name = key
    return series


# ---------------------------------------------------------------------------
# Series mensuales (nivel agregado)
# ---------------------------------------------------------------------------
def load_series_long() -> pd.DataFrame:
    """Devuelve todas las series mensuales en formato largo.

    Columnas: fecha, anio, mes, serie_key, serie, valor.
    """
    raw = _raw()
    frames = []
    for key in SERIES_KEYS:
        s = _series_from_raw(raw, key)
        frame = pd.DataFrame(
            {
                "fecha": s.index,
                "valor": s.values.astype(float),
                "serie_key": key,
                "serie": lab2_data.series_label(key),
            }
        )
        frames.append(frame)
    df = pd.concat(frames, ignore_index=True)
    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["mes_nombre"] = df["mes"].map(lambda m: MONTH_NAMES_ES[m - 1])
    return df


def series_label(key: str) -> str:
    return lab2_data.series_label(key)


# ---------------------------------------------------------------------------
# Desgloses (para gráficos de composición y exploración)
# ---------------------------------------------------------------------------
def _reference_raw() -> pd.DataFrame:
    """Población de referencia (turistas/excursionistas no residentes) con fecha."""
    return lab2_data._reference_population(_raw())


def load_breakdown(dimension: str) -> pd.DataFrame:
    """Serie mensual de visitantes desglosada por una dimensión categórica.

    dimension: 'Vía' o 'Región dos'.
    Columnas: fecha, anio, mes, categoria, valor.
    """
    ref = _reference_raw()
    grouped = (
        ref.groupby(["date", dimension])["Viajero"].sum().reset_index()
    )
    grouped = grouped.rename(columns={"date": "fecha", dimension: "categoria", "Viajero": "valor"})
    grouped["anio"] = grouped["fecha"].dt.year
    grouped["mes"] = grouped["fecha"].dt.month
    # Limpia categorías ruidosas ('0', nulos).
    grouped = grouped[~grouped["categoria"].isin(["0", 0])]
    grouped = grouped.dropna(subset=["categoria"])
    return grouped


def load_country_breakdown(top_n: int = 12) -> pd.DataFrame:
    """Visitantes por país/agrupación de residencia (top_n globales + 'Otros')."""
    ref = _reference_raw()
    col = "Agrupación Residencia"
    totals = ref.groupby(col)["Viajero"].sum().sort_values(ascending=False)
    top = list(totals.head(top_n).index)
    ref = ref.copy()
    ref["pais"] = np.where(ref[col].isin(top), ref[col], "Otros")
    grouped = ref.groupby(["date", "pais"])["Viajero"].sum().reset_index()
    grouped = grouped.rename(columns={"date": "fecha", "Viajero": "valor"})
    grouped["anio"] = grouped["fecha"].dt.year
    grouped["mes"] = grouped["fecha"].dt.month
    return grouped


# ---------------------------------------------------------------------------
# Modelos: predicciones y métricas (Laboratorio 2)
# ---------------------------------------------------------------------------
# Registro de modelos disponibles por serie.
# Cada entrada: (id_modelo, etiqueta, fuente_npz, clave_en_npz)
MODEL_REGISTRY = {
    "total": [
        ("total__simple", "LSTM simple", "test", "total__simple"),
        ("total__stacked", "LSTM apilado", "test", "total__stacked"),
        ("lstm_global_catch22", "LSTM global (catch22)", "global", "total"),
    ],
    "air_entry": [
        ("air_entry__simple", "LSTM simple", "test", "air_entry__simple"),
        ("air_entry__stacked", "LSTM apilado", "test", "air_entry__stacked"),
    ],
}

MODELED_SERIES = list(MODEL_REGISTRY.keys())


def _load_npz():
    test = np.load(OUTPUTS / "metrics" / "test_predictions.npz", allow_pickle=True)
    glob = np.load(OUTPUTS / "metrics" / "lstm_global_catch22_predictions.npz", allow_pickle=True)
    return test, glob


def load_predictions() -> pd.DataFrame:
    """Predicciones de la ventana de prueba, en formato largo.

    Columnas: fecha, serie_key, serie, modelo_id, modelo, observado, predicho.
    """
    test_npz, glob_npz = _load_npz()
    series_long = load_series_long()
    rows = []
    for serie_key, models in MODEL_REGISTRY.items():
        serie = series_label(serie_key)
        obs_series = (
            series_long[series_long["serie_key"] == serie_key]
            .set_index("fecha")["valor"]
            .loc[TEST_START:TEST_END]
        )
        test_dates = obs_series.index
        for modelo_id, modelo, fuente, key in models:
            arr = test_npz[key] if fuente == "test" else glob_npz[key]
            arr = np.asarray(arr, dtype=float)
            n = min(len(test_dates), len(arr))
            for i in range(n):
                rows.append(
                    {
                        "fecha": test_dates[i],
                        "serie_key": serie_key,
                        "serie": serie,
                        "modelo_id": modelo_id,
                        "modelo": modelo,
                        "observado": float(obs_series.iloc[i]),
                        "predicho": float(arr[i]),
                    }
                )
    df = pd.DataFrame(rows)
    df["error"] = df["observado"] - df["predicho"]
    df["error_abs"] = df["error"].abs()
    df["error_pct"] = np.where(
        df["observado"] != 0, df["error"] / df["observado"] * 100, np.nan
    )
    return df


def load_metrics() -> pd.DataFrame:
    """Tabla comparativa de métricas por modelo (MAE, RMSE, MAPE, MASE)."""
    tuning = pd.read_csv(OUTPUTS / "metrics" / "lstm_tuning_summary.csv")
    tuning = tuning.rename(columns={"series_label": "serie"})
    tuning["modelo"] = tuning["architecture"].map(
        {"simple": "LSTM simple", "stacked": "LSTM apilado"}
    )
    tuning["modelo_id"] = tuning["series_key"].astype(str) + "__" + tuning["architecture"].astype(str)
    cols = ["serie", "serie_key", "modelo", "modelo_id", "mae", "rmse", "mape", "mase"]
    tuning = tuning.rename(columns={"series_key": "serie_key"})[cols]

    glob = pd.read_csv(OUTPUTS / "metrics" / "lstm_global_catch22_metrics.csv")
    glob = glob.rename(columns={"modelo": "modelo_id", "serie": "serie"})
    glob["modelo"] = "LSTM global (catch22)"
    glob["serie_key"] = "total"
    glob = glob[["serie", "serie_key", "modelo", "modelo_id", "mae", "rmse", "mape", "mase"]]

    out = pd.concat([tuning, glob], ignore_index=True)
    # Solo conserva series que se muestran en el tablero.
    out = out[out["serie_key"].isin(MODELED_SERIES)].reset_index(drop=True)
    return out


def load_tuning_trials() -> pd.DataFrame:
    """Ensayos de búsqueda de hiperparámetros (val_loss por ensayo)."""
    frames = []
    mapping = {
        "total_simple_trials.csv": ("total", "LSTM simple"),
        "total_stacked_trials.csv": ("total", "LSTM apilado"),
        "air_entry_simple_trials.csv": ("air_entry", "LSTM simple"),
        "air_entry_stacked_trials.csv": ("air_entry", "LSTM apilado"),
    }
    tuning_dir = OUTPUTS / "tuning"
    for fname, (serie_key, modelo) in mapping.items():
        fpath = tuning_dir / fname
        if not fpath.exists():
            continue
        t = pd.read_csv(fpath)
        t["serie_key"] = serie_key
        t["serie"] = series_label(serie_key)
        t["modelo"] = modelo
        frames.append(t)
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    return df


# ---------------------------------------------------------------------------
# Perfil de series (catch22) — exploración avanzada
# ---------------------------------------------------------------------------
def load_catch22_pca() -> pd.DataFrame:
    scores = pd.read_csv(OUTPUTS / "metrics" / "catch22_pca_scores.csv")
    clusters = pd.read_csv(OUTPUTS / "metrics" / "catch22_clusters.csv")
    df = scores.merge(clusters, on="serie", how="left")
    return df


def load_catch22_distance() -> pd.DataFrame:
    return pd.read_csv(OUTPUTS / "metrics" / "catch22_series_distance.csv", index_col=0)


def catch22_pca_variance() -> list[float]:
    txt = (OUTPUTS / "metrics" / "catch22_pca_explained_variance.txt").read_text().strip()
    return [float(x) for x in txt.split(",")]
