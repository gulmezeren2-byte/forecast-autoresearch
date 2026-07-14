"""THE AGENT'S FILE — the only file the agent may edit.

Contract:
    forecast_one(history) -> float
    history: 1-D numpy array of past monthly demand for ONE SKU (oldest first,
             always >= 12 values). Return the forecast for the NEXT month.
    Must be deterministic, must not read any file, must not import model-external
    state. Total scoring budget across all calls: see run.py BUDGET_SECONDS.

Model of record: run 3 (cycle 1 champion, holdout FVA +7.62).
Pattern-aware split: SKUs with >20% zero months get a 12-month mean;
the rest get seasonal-index + SES. Runs 4-5 explored refinements and were
refused/reverted - see journal/JOURNAL.md.
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
    return float(max(0.0, _ses(deseasonalized) * idx[n % SEASON]))
