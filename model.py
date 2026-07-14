"""THE AGENT'S FILE — the only file the agent may edit.

Contract:
    forecast_one(history) -> float
    history: 1-D numpy array of past monthly demand for ONE SKU (oldest first,
             always >= 12 values). Return the forecast for the NEXT month.
    Must be deterministic, must not read any file, must not import model-external
    state. Total scoring budget across all calls: see run.py BUDGET_SECONDS.

Experiment 3: pattern-aware split (directive step 3).
Intermittent/lumpy detection from the history alone (zero share > 0.20):
those SKUs get a calm 12-month mean; smooth/erratic SKUs keep the run-1
seasonal-index + SES logic (damped trend retired after run 2).
"""

from __future__ import annotations

import numpy as np

SEASON = 12
ZERO_SHARE_CUT = 0.20


def _ses(x: np.ndarray, alpha: float = 0.3) -> float:
    level = x[0]
    for v in x[1:]:
        level = alpha * v + (1 - alpha) * level
    return float(level)


def forecast_one(history: np.ndarray) -> float:
    h = np.asarray(history, dtype=float)
    n = len(h)
    if (h == 0).mean() > ZERO_SHARE_CUT:
        return float(h[-SEASON:].mean())  # intermittent/lumpy: calm long-window mean
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
