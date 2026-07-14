"""Protocol determinism tests - the numbers must reproduce exactly, every time."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import prepare  # noqa: E402
import run  # noqa: E402


def test_generator_is_deterministic():
    a, b = prepare.generate_full(), prepare.generate_full()
    assert a.equals(b)
    assert a.sku.nunique() == 24
    assert a.month.nunique() == 48


def test_naive_fva_is_zero_by_construction():
    res = run.evaluate(lambda h: float(h[-1]))
    assert res["dev_fva"] == 0.0
    assert res["holdout_fva"] == 0.0


def test_reference_bar_reproduces_exactly():
    res = run.evaluate(run.REFERENCES["ref: seasonal SES"])
    assert res["holdout_fva"] == 6.79
    assert res["dev_fva"] == 3.98


def test_model_contract():
    fn = run.load_model()
    out = fn(np.array([10.0] * 12))
    assert np.isfinite(out)


def test_holdout_not_on_disk():
    train = (ROOT / "data" / "train.csv").read_text(encoding="utf-8")
    full = prepare.generate_full()
    holdout_months = sorted(full.month.unique())[prepare.TRAIN_MONTHS:]
    for m in holdout_months:
        assert m not in train, f"holdout month {m} leaked into train.csv"
