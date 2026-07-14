"""THE AGENT'S FILE — the only file the agent may edit.

Contract:
    forecast_one(history) -> float
    history: 1-D numpy array of past monthly demand for ONE SKU (oldest first,
             always >= 12 values). Return the forecast for the NEXT month.
    Must be deterministic, must not read any file, must not import model-external
    state. Total scoring budget across all calls: see run.py BUDGET_SECONDS.

Cycle 2, experiment 3: per-series alpha for the smooth branch.
Croston/SBA retired (runs 6-7: holdout supports the plain mean). Intermittent
branch back to the champion's 12-month mean. On the smooth branch, SES alpha
is chosen per series from {0.1..0.5} by one-step error over the series' OWN
history (deseasonalized) - never against dev scores.
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
    overall = h.mean() if h.mean() > 0 else 1.0
    idx = np.array([
        h[m == k].mean() / overall if h[m == k].mean() > 0 else 1.0
        for k in range(SEASON)
    ])
    idx = np.where(idx <= 0, 1.0, idx)
    deseasonalized = h / idx[m]
    return float(max(0.0, _ses_tuned(deseasonalized) * idx[n % SEASON]))
