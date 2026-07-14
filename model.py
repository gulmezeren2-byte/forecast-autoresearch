"""THE AGENT'S FILE — the only file the agent may edit.

Contract:
    forecast_one(history) -> float
    history: 1-D numpy array of past monthly demand for ONE SKU (oldest first,
             always >= 12 values). Return the forecast for the NEXT month.
    Must be deterministic, must not read any file, must not import model-external
    state. Total scoring budget across all calls: see run.py BUDGET_SECONDS.

Cycle 2, experiment 4: robust seasonal indices (run 8 + medians).
Per-month indices computed from medians instead of means, so a single
outlier month cannot distort a slot's index. Everything else as run 8.
"""

from __future__ import annotations

import numpy as np

SEASON = 12
ZERO_SHARE_CUT = 0.20
ALPHAS = (0.1, 0.2, 0.3, 0.4, 0.5)


def _ses(x: np.ndarray, alpha: float) -> float:
    level = x[0]
    for v in x[1:]:
        level = alpha * v + (1 - alpha) * level
    return float(level)


def _ses_tuned(x: np.ndarray) -> float:
    best_a, best_err = 0.3, np.inf
    for a in ALPHAS:
        level, err = x[0], 0.0
        for v in x[1:]:
            err += abs(v - level)
            level = a * v + (1 - a) * level
        if err < best_err:
            best_a, best_err = a, err
    return _ses(x, best_a)


def forecast_one(history: np.ndarray) -> float:
    h = np.asarray(history, dtype=float)
    n = len(h)
    if (h == 0).mean() > ZERO_SHARE_CUT:
        return float(h[-SEASON:].mean())  # intermittent/lumpy: calm 12-month mean
    if n < 2 * SEASON:
        return _ses(h)
    m = np.arange(n) % SEASON
    overall = np.median(h) if np.median(h) > 0 else (h.mean() if h.mean() > 0 else 1.0)
    idx = np.array([
        np.median(h[m == k]) / overall if np.median(h[m == k]) > 0 else 1.0
        for k in range(SEASON)
    ])
    idx = np.where(idx <= 0, 1.0, idx)
    deseasonalized = h / idx[m]
    return float(max(0.0, _ses_tuned(deseasonalized) * idx[n % SEASON]))
