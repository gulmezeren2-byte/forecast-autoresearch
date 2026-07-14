"""THE AGENT'S FILE — the only file the agent may edit.

Contract:
    forecast_one(history) -> float
    history: 1-D numpy array of past monthly demand for ONE SKU (oldest first,
             always >= 12 values). Return the forecast for the NEXT month.
    Must be deterministic, must not read any file, must not import model-external
    state. Total scoring budget across all calls: see run.py BUDGET_SECONDS.

Cycle 2, experiment 2: Croston + SBA bias correction.
Croston's estimator is positively biased; Syntetos-Boylan approximation
multiplies the rate by (1 - alpha/2). Everything else as experiment 6.
"""

from __future__ import annotations

import numpy as np

SEASON = 12
ZERO_SHARE_CUT = 0.20
CROSTON_ALPHA = 0.15


def _ses(x: np.ndarray, alpha: float = 0.3) -> float:
    level = x[0]
    for v in x[1:]:
        level = alpha * v + (1 - alpha) * level
    return float(level)


def _croston(h: np.ndarray, alpha: float = CROSTON_ALPHA) -> float:
    size = interval = None
    gap = 1
    for v in h:
        if v > 0:
            size = v if size is None else alpha * v + (1 - alpha) * size
            interval = gap if interval is None else alpha * gap + (1 - alpha) * interval
            gap = 1
        else:
            gap += 1
    if size is None:
        return 0.0
    return float((size / max(interval, 1e-9)) * (1 - alpha / 2))  # SBA correction


def forecast_one(history: np.ndarray) -> float:
    h = np.asarray(history, dtype=float)
    n = len(h)
    if (h == 0).mean() > ZERO_SHARE_CUT:
        return _croston(h)  # intermittent/lumpy: Croston's method
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
    return float(max(0.0, _ses(deseasonalized) * idx[n % SEASON]))
