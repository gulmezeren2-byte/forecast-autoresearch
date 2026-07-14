"""THE AGENT'S FILE — the only file the agent may edit.

Contract:
    forecast_one(history) -> float
    history: 1-D numpy array of past monthly demand for ONE SKU (oldest first,
             always >= 12 values). Return the forecast for the NEXT month.
    Must be deterministic, must not read any file, must not import model-external
    state. Total scoring budget across all calls: see run.py BUDGET_SECONDS.

The journey starts at naive — FVA = 0.0 by construction. Beat it honestly.
"""

from __future__ import annotations

import numpy as np


def forecast_one(history: np.ndarray) -> float:
    return float(history[-1])  # naive: next month = last month
