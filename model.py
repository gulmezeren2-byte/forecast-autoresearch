"""THE AGENT'S FILE — the only file the agent may edit.

Contract:
    forecast_one(history) -> float
    history: 1-D numpy array of past monthly demand for ONE SKU (oldest first,
             always >= 12 values). Return the forecast for the NEXT month.
    Must be deterministic, must not read any file, must not import model-external
    state. Total scoring budget across all calls: see run.py BUDGET_SECONDS.

Cycle 2, experiment 5: in-history window selection for the intermittent branch.
Medians reverted (run 9 regression). Run 8 kept; additionally the intermittent
branch's mean window is chosen per series from {6, 12, 24, all} by one-step
error over the series' OWN history - the same legitimate mechanism that made
run 8 the champion, applied to the other branch.
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


def _windowed_mean_tuned(h: np.ndarray) -> float:
    n = len(h)
    windows = [w for w in (6, 12, 24) if w < n] + [n]
    best_w, best_err = windows[-1], np.inf
    start = max(SEASON, n - SEASON)  # evaluate over the last year of history
    for w in windows:
        err = 0.0
        for t in range(start, n):
            err += abs(h[max(0, t - w):t].mean() - h[t])
        if err < best_err:
            best_w, best_err = w, err
    return float(h[-best_w:].mean())


def forecast_one(history: np.ndarray) -> float:
    h = np.asarray(history, dtype=float)
    n = len(h)
    if (h == 0).mean() > ZERO_SHARE_CUT:
        return _windowed_mean_tuned(h)  # intermittent/lumpy: in-history window choice
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
