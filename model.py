"""THE AGENT'S FILE — the only file the agent may edit.

Contract:
    forecast_one(history) -> float
    history: 1-D numpy array of past monthly demand for ONE SKU (oldest first,
             always >= 12 values). Return the forecast for the NEXT month.
    Must be deterministic, must not read any file, must not import model-external
    state. Total scoring budget across all calls: see run.py BUDGET_SECONDS.

Experiment 2: damped-trend Holt on the deseasonalized level (directive step 2).
Same seasonal indices as run 1; the deseasonalized series is smoothed with
Holt's level+trend (alpha=0.3, beta=0.1) and the trend is damped (phi=0.85)
before reseasonalizing.
"""

from __future__ import annotations

import numpy as np

SEASON = 12
ALPHA, BETA, PHI = 0.3, 0.1, 0.85


def _damped_holt(x: np.ndarray) -> float:
    level, trend = x[0], 0.0
    for v in x[1:]:
        prev = level
        level = ALPHA * v + (1 - ALPHA) * (level + PHI * trend)
        trend = BETA * (level - prev) + (1 - BETA) * PHI * trend
    return float(level + PHI * trend)


def forecast_one(history: np.ndarray) -> float:
    h = np.asarray(history, dtype=float)
    n = len(h)
    if n < 2 * SEASON:
        return _damped_holt(h)
    m = np.arange(n) % SEASON
    overall = h.mean() if h.mean() > 0 else 1.0
    idx = np.array([
        h[m == k].mean() / overall if h[m == k].mean() > 0 else 1.0
        for k in range(SEASON)
    ])
    idx = np.where(idx <= 0, 1.0, idx)
    deseasonalized = h / idx[m]
    return float(max(0.0, _damped_holt(deseasonalized) * idx[n % SEASON]))
