"""Pronóstico horario de MP2.5 y evaluación reproducible del Avance 3."""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/processed/dataset_horario_cqp_2023_2025.csv"
TIME = "fecha_hora"
STATION = "estacion"
TARGET = "mp25_ug_m3"
LAG = "mp25_lag_1h"
GROUPS = {
    "MP2.5 · 1 h antes": [LAG],
    "MP2.5 · 3 h antes": ["mp25_lag_3h"],
    "MP2.5 · 24 h antes": ["mp25_lag_24h"],
    "MP2.5 · media previa 6 h": ["mp25_media_6h"],
    "MP10 · 1 h antes": ["mp10_lag_1h"],
    "SO₂ · 1 h antes": ["so2_lag_1h"],
    "Velocidad del viento · 1 h antes": ["viento_vel_lag_1h"],
    "Dirección del viento · 1 h antes": ["viento_sin", "viento_cos"],
    "Hora del día": ["hora_sin", "hora_cos"],
    "Mes": ["mes_sin", "mes_cos"],
    "Fin de semana": ["fin_semana"],
    "Estación": [STATION],
}
FEATURES = [column for group in GROUPS.values() for column in group]
INK, BLUE, GREEN, ORANGE = "#172e3a", "#326a9b", "#007e70", "#b95a32"
MODELS = ["Ridge", "Random Forest"]


def preparar_datos(path):
    lags = {
        LAG: (TARGET, 1),
        "mp25_lag_3h": (TARGET, 3),
        "mp25_lag_24h": (TARGET, 24),
        "mp10_lag_1h": ("mp10_ug_m3n", 1),
        "so2_lag_1h": ("so2_ppb", 1),
        "viento_vel_lag_1h": ("velocidad_viento_m_s", 1),
        "viento_dir_lag_1h": ("direccion_viento_grados", 1),
    }
    columns = [TIME, STATION, *dict.fromkeys(col for col, _ in lags.values())]
    raw = pd.read_csv(path, usecols=columns, parse_dates=[TIME])
    if raw[[TIME, STATION]].isna().any().any() or raw.duplicated([STATION, TIME]).any():
        raise ValueError("El CSV debe contener una fila por estación y hora válida.")
    if not raw[TIME].eq(raw[TIME].dt.floor("h")).all():
        raise ValueError("Todas las marcas de tiempo deben corresponder a horas enteras.")

    # Buscamos la hora exacta para no saltarnos horas sin datos.
    raw = raw.sort_values([STATION, TIME]).reset_index(drop=True)
    history = raw.set_index([STATION, TIME])
    frame = raw[[STATION, TIME, TARGET]].copy()
    for feature, (column, hours) in lags.items():
        keys = pd.MultiIndex.from_arrays([raw[STATION], raw[TIME] - pd.Timedelta(hours=hours)])
        frame[feature] = history[column].reindex(keys).to_numpy()

    # Promediamos las seis horas anteriores de la misma estación.
    rolling = raw.groupby(STATION).rolling("6h", on=TIME, closed="left", min_periods=2)[TARGET].mean()
    frame["mp25_media_6h"] = rolling.reindex(history.index).to_numpy()
    angle = np.deg2rad(frame.pop("viento_dir_lag_1h"))
    frame["viento_sin"], frame["viento_cos"] = np.sin(angle), np.cos(angle)
    for name, angle in {
        "hora": 2 * np.pi * frame[TIME].dt.hour / 24,
        "mes": 2 * np.pi * (frame[TIME].dt.month - 1) / 12,
    }.items():
        frame[f"{name}_sin"], frame[f"{name}_cos"] = np.sin(angle), np.cos(angle)
    frame["fin_semana"] = frame[TIME].dt.dayofweek.ge(5).astype(int)
    sample = frame.dropna(subset=[TARGET, LAG]).sort_values([TIME, STATION]).reset_index(drop=True)
    return sample, len(raw)


def construir_modelos(jobs):
    models = {}
    for name, reg in [
        ("Ridge", Ridge(alpha=10.0)),
        ("Random Forest", RandomForestRegressor(
            n_estimators=150, max_depth=12, min_samples_leaf=10, n_jobs=jobs, random_state=42
        )),
    ]:
        numeric = [column for column in FEATURES if column != STATION]
        transform = ColumnTransformer([
            ("num", Pipeline([
                ("imputar", SimpleImputer(strategy="median", keep_empty_features=True)),
                ("escalar", StandardScaler()),
            ]), numeric),
            ("estacion", OneHotEncoder(handle_unknown="ignore", sparse_output=False), [STATION]),
        ])
        models[name] = Pipeline([("preparar", transform), ("regresor", reg)])
    return models


def metricas(real, pred):
    return {
        "MAE": mean_absolute_error(real, pred),
        "RMSE": np.sqrt(mean_squared_error(real, pred)),
        "R2": r2_score(real, pred),
    }


def evaluar(train, test, jobs):
    hours = train[TIME].drop_duplicates().to_numpy()
    splits = [
        (train[TIME].isin(hours[a]), train[TIME].isin(hours[b]))
        for a, b in TimeSeriesSplit(n_splits=5).split(hours)
    ]
    assert all(train.loc[a, TIME].max() < train.loc[b, TIME].min() for a, b in splits)
    models = construir_modelos(jobs)
    scores, forecasts = {}, {}
    for name, model in {"Persistencia": None, **models}.items():
        def predict(rows):
            return rows[LAG].to_numpy() if model is None else model.predict(rows[FEATURES])

        cv = []
        for a, b in splits:
            fit, val = train.loc[a], train.loc[b]
            if model is not None:
                model.fit(fit[FEATURES], fit[TARGET])
            cv.append(metricas(val[TARGET], predict(val)))
        cv = pd.DataFrame(cv)
        if model is not None:
            model.fit(train[FEATURES], train[TARGET])
        forecasts[name] = predict(test)
        scores[name] = {
            "train": metricas(train[TARGET], predict(train)),
            "cv_mean": cv.mean().to_dict(),
            "cv_sd": cv.std(ddof=1).to_dict(),
            "test": metricas(test[TARGET], forecasts[name]),
        }
    winner = min(MODELS, key=lambda name: scores[name]["cv_mean"]["RMSE"])
    return scores, forecasts, winner, models[winner]


def shap_por_permutaciones(model, sample, train, paths=40):
    """Aproximamos los valores SHAP con permutaciones.

    Usamos filas de entrenamiento como referencia. Agrupamos seno y coseno
    para medir juntos los aportes de cada variable circular.
    """
    rng = np.random.default_rng(43)
    groups = list(GROUPS.values())
    background = train[FEATURES].sample(n=paths, random_state=43, replace=len(train) < paths)
    base = float(model.predict(background).mean())
    contributions = np.zeros((len(sample), len(groups)))
    for _, row in background.iterrows():
        order = rng.permutation(len(groups))
        hybrid = pd.DataFrame({col: [row[col]] * len(sample) for col in FEATURES})
        steps = [hybrid.copy()]
        for group_index in order:
            columns = groups[group_index]
            hybrid[columns] = sample[columns].to_numpy()
            steps.append(hybrid.copy())
        predictions = model.predict(pd.concat(steps, ignore_index=True)).reshape(len(steps), len(sample))
        contributions[:, order] += np.diff(predictions, axis=0).T / paths
    np.testing.assert_allclose(base + contributions.sum(axis=1), model.predict(sample[FEATURES]), atol=1e-8)
    return base, pd.DataFrame(contributions, columns=GROUPS)


def casos_de_prueba(test, pred):
    y = test[TARGET].to_numpy()
    res = y - pred
    q65, q90, q95 = np.quantile(y, [0.65, 0.90, 0.95])
    candidates = np.flatnonzero((y >= q65) & (y <= q90))
    accurate = candidates[np.argmin(np.abs(res[candidates]))]
    upper = np.flatnonzero((y >= q95) & (res > 0))
    if len(upper):
        return int(accurate), int(upper[np.argmax(res[upper])]), "Mayor subestimación entre valores ≥ P95"
    worst = int(np.argmax(np.abs(res)))
    if worst == accurate:
        candidates = candidates[candidates != worst]
        accurate = candidates[np.argmin(np.abs(res[candidates]))]
    return int(accurate), worst, "Mayor error absoluto"


def graficos_rendimiento(test, forecasts, winner, error_index, out):
    y = test[TARGET].to_numpy()
    all_predictions = np.concatenate([forecasts[name] for name in MODELS])
    low, high = min(0, y.min(), all_predictions.min()), max(y.max(), all_predictions.max())
    lo, hi = low - 3, high + 4
    for residuals, filename in [(False, "real_predicho"), (True, "residuos")]:
        fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.35), sharex=True, sharey=True, layout="constrained")
        for ax, name, color in zip(axes, MODELS, (BLUE, GREEN)):
            pred = forecasts[name]
            xx, yy = (pred, y - pred) if residuals else (y, pred)
            ax.scatter(xx, yy, s=9, color=color, alpha=0.14, edgecolors="none", rasterized=True)
            if residuals:
                ax.axhline(0, ls="--", color=INK, lw=1.2)
            else:
                ax.plot([lo, hi], [lo, hi], ls="--", color=INK, lw=1.2)
                ax.set_ylim(lo, hi)
            ax.scatter(xx[error_index], yy[error_index], s=56, color=ORANGE, edgecolor="white", zorder=4)
            ax.set_xlim(lo, hi)
            ax.set_title(name, loc="left", fontweight="bold", fontsize=14)
            ax.set_xlabel("Predicción (µg/m³)" if residuals else "Medición real (µg/m³)")
            ax.grid(alpha=.20)
            ax.set_axisbelow(True)
        axes[0].set_ylabel("Residuo real − predicho (µg/m³)" if residuals else "Predicción (µg/m³)")
        fig.savefig(out / f"{filename}.png", dpi=180)
        plt.close(fig)


def graficos_shap(shap_values, base, cases, out):
    importance = shap_values.abs().mean().nlargest(7).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8.2, 4.0), layout="constrained")
    ax.barh(importance.index, importance, color=GREEN)
    ax.set_xlabel("Media de |SHAP| (µg/m³)")
    ax.grid(axis="x", alpha=.2)
    ax.set_axisbelow(True)
    fig.savefig(out / "shap_global.png", dpi=180)
    plt.close(fig)

    for i, case in enumerate(cases, 1):
        values = pd.Series(case["shap"], dtype=float)
        top = values.loc[values.abs().nlargest(5).index]
        others = values.drop(top.index).sum()
        top = pd.concat([top, pd.Series({"Otras variables": others})])
        labels = ["Valor base", *top.index, "Predicción"]
        end = np.r_[base, base + top.cumsum().to_numpy(), case["pred"]]
        start = np.r_[0, end[:-2], 0]
        fig, ax = plt.subplots(figsize=(8.8, 4.8), layout="constrained")
        for j, (a, b) in enumerate(zip(start, end)):
            anchor = j in (0, len(labels) - 1)
            color = INK if anchor else (GREEN if b >= a else ORANGE)
            ax.barh(j, abs(b - a), left=min(a, b), height=.59, color=color)
            label = f"{b:.1f}" if anchor else f"{b - a:+.2f}"
            ax.text(max(a, b) + .55, j, label.replace(".", ","), va="center", fontsize=11, color=INK)
            if j < len(labels) - 1:
                ax.vlines(b, j + .3, j + .7, color="#92a3a6", lw=1)
        ax.set_yticks(range(len(labels)), labels)
        ax.invert_yaxis()
        ax.set_xlim(min(0, start.min(), end.min()), max(start.max(), end.max()) + 5)
        ax.set_xlabel("MP2.5 predicho (µg/m³)")
        ax.grid(axis="x", alpha=.2)
        ax.set_axisbelow(True)
        fig.savefig(out / f"shap_caso_{i}.png", dpi=180)
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--out", type=Path, default=ROOT / "reports/avance3")
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
        "axes.labelcolor": INK, "axes.edgecolor": "#a2b0b2", "axes.spines.top": False,
        "axes.spines.right": False, "xtick.color": INK, "ytick.color": INK,
    })

    frame, raw_count = preparar_datos(args.data)
    train = frame.loc[frame[TIME].dt.year.isin([2023, 2024])].reset_index(drop=True)
    test = frame.loc[frame[TIME].dt.year.eq(2025)].reset_index(drop=True)
    if train.empty or test.empty:
        raise ValueError("Se requieren observaciones elegibles de 2023–2024 y 2025.")
    scores, forecasts, winner, model = evaluar(train, test, args.jobs)
    pred = forecasts[winner]
    accurate, error, error_rule = casos_de_prueba(test, pred)
    sample = test.sample(n=min(320, len(test)), random_state=42)
    explain = pd.concat([sample, test.iloc[[accurate, error]]], ignore_index=True)
    base, shap_values = shap_por_permutaciones(model, explain, train)
    global_values = shap_values.iloc[:len(sample)]
    cases = []
    for i, idx in enumerate([accurate, error]):
        row = test.iloc[idx]
        cases.append({
            "station": row[STATION], "time": str(row[TIME]), "real": row[TARGET],
            "pred": pred[idx], "residual": row[TARGET] - pred[idx], "lag1": row[LAG],
            "mean6": None if pd.isna(row["mp25_media_6h"]) else row["mp25_media_6h"],
            "shap": shap_values.iloc[len(sample) + i].to_dict(),
        })

    threshold = test[TARGET].quantile(.95)
    upper = test[TARGET].ge(threshold)
    lag_split = sample[LAG].median()
    result = {
        "raw": raw_count, "train_n": len(train), "test_n": len(test),
        "stations": sorted(frame[STATION].unique().tolist()), "winner": winner, "scores": scores,
        "upper_p95": threshold, "upper_n": int(upper.sum()),
        "bias": {name: float((test[TARGET] - p).mean()) for name, p in forecasts.items()},
        "upper_bias": {name: float((test.loc[upper, TARGET] - p[upper]).mean()) for name, p in forecasts.items()},
        "upper_mae": {name: float(np.abs(test.loc[upper, TARGET] - p[upper]).mean()) for name, p in forecasts.items()},
        "shap_n": len(sample), "shap_base": base, "cases": cases, "error_rule": error_rule,
        "shap_global": global_values.abs().mean().sort_values(ascending=False).to_dict(),
        "lag_split": lag_split,
        "lag_shap_low": float(global_values.loc[sample[LAG].to_numpy() <= lag_split, "MP2.5 · 1 h antes"].mean()),
        "lag_shap_high": float(global_values.loc[sample[LAG].to_numpy() > lag_split, "MP2.5 · 1 h antes"].mean()),
    }
    graficos_rendimiento(test, forecasts, winner, error, out)
    graficos_shap(global_values, base, cases, out)
    rows = [
        {"modelo": name, "conjunto": split, **values}
        for name, by_split in scores.items() for split, values in by_split.items()
    ]
    pd.DataFrame(rows).to_csv(out / "metricas.csv", index=False)
    (out / "resultados.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


if __name__ == "__main__":
    main()
