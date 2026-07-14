"""PROTOCOL FILE — DO NOT EDIT. The experiment is only meaningful if this file
and run.py stay frozen; run.py records a hash of both into every leaderboard row.

Generates the fixed, seeded demand universe:
- 24 SKUs x 48 months (2022-07 .. 2026-06), four demand patterns
- Writes data/train.csv        -> the first 42 months (agent-visible)
- The last 6 months (holdout) are NEVER written to disk; run.py regenerates
  the full series from the same seed at scoring time.

Run once: python prepare.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20260714
N_MONTHS = 48
TRAIN_MONTHS = 42
HOLDOUT_MONTHS = N_MONTHS - TRAIN_MONTHS
MONTHS = pd.date_range("2022-07-01", periods=N_MONTHS, freq="MS")


def generate_full() -> pd.DataFrame:
    """The complete 48-month universe. Deterministic for SEED."""
    rng = np.random.default_rng(SEED)
    rows = []
    profiles = [("smooth", 8), ("erratic", 6), ("intermittent", 6), ("lumpy", 4)]
    i = 0
    for pattern, count in profiles:
        for _ in range(count):
            i += 1
            if pattern == "smooth":
                base = rng.uniform(150, 900)
                trend = rng.uniform(-0.015, 0.03) / 12
                amp = rng.uniform(0.12, 0.30)
                phase = rng.uniform(0, 2 * np.pi)
                t = np.arange(N_MONTHS)
                season = 1 + amp * np.sin(2 * np.pi * t / 12 + phase)
                noise = rng.normal(1, rng.uniform(0.07, 0.14), N_MONTHS)
                qty = np.maximum(0, base * (1 + trend * t) * season * noise)
            elif pattern == "erratic":
                base = rng.uniform(80, 500)
                qty = np.maximum(0, base * rng.normal(1, rng.uniform(0.35, 0.55), N_MONTHS))
            elif pattern == "intermittent":
                p = rng.uniform(0.45, 0.7)
                size = rng.lognormal(np.log(rng.uniform(15, 70)), 0.4, N_MONTHS)
                qty = np.where(rng.random(N_MONTHS) < p, size, 0)
            else:  # lumpy
                p = rng.uniform(0.3, 0.5)
                size = rng.lognormal(np.log(rng.uniform(40, 180)), 0.85, N_MONTHS)
                qty = np.where(rng.random(N_MONTHS) < p, size, 0)
            for m, q in zip(MONTHS, np.round(qty)):
                rows.append((f"SKU-{i:02d}", m.date().isoformat(), float(q), pattern))
    return pd.DataFrame(rows, columns=["sku", "month", "qty", "pattern"])


def main() -> None:
    full = generate_full()
    train_cutoff = MONTHS[TRAIN_MONTHS - 1].date().isoformat()
    train = full[full.month <= train_cutoff]
    import os

    os.makedirs("data", exist_ok=True)
    train.to_csv("data/train.csv", index=False)
    print(
        f"data/train.csv written: {train.sku.nunique()} SKUs x {TRAIN_MONTHS} months "
        f"(holdout: {HOLDOUT_MONTHS} months, never materialized - run.py regenerates it)"
    )


if __name__ == "__main__":
    main()
