"""PROTOCOL FILE — DO NOT EDIT. Scores model.py against the fixed protocol.

Usage:
    python run.py --note "what I tried"     # score current model.py, append leaderboard
    python run.py --reference               # score the built-in reference models once
    python run.py --chart                   # redraw charts/leaderboard.svg from leaderboard.csv

Protocol (frozen):
- DEV score: rolling-origin, one-month-ahead over the LAST 6 months of train.csv.
  The agent may iterate against this number freely.
- HOLDOUT score: the 6 months after train.csv, regenerated in-memory from the
  seed in prepare.py; never written to disk. One-month-ahead, expanding window.
- Single metric: FVA = naive_WMAPE - model_WMAPE, in percentage points.
  Positive = the model adds value over shipping last month's number.
- Budget: BUDGET_SECONDS wall-clock for all forecast calls per scoring pass.
- Tamper evidence: every leaderboard row records sha256(prepare.py|run.py)[:12]
  and model.py's sha256[:12]. Rows with a different protocol hash are not
  comparable and the leaderboard marks them.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import sys
import time

import numpy as np
import pandas as pd

import prepare

BUDGET_SECONDS = 120.0
DEV_H = 6
LEADERBOARD_CSV = "leaderboard.csv"
LEADERBOARD_MD = "leaderboard.md"


# ---------------------------------------------------------------- hashing ---
def _sha(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def protocol_hash() -> str:
    return hashlib.sha256((_sha("prepare.py") + _sha("run.py")).encode()).hexdigest()[:12]


# ---------------------------------------------------------------- scoring ---
def _wmape(errs: list[float], actuals: list[float]) -> float:
    return sum(abs(e) for e in errs) / max(1e-9, sum(actuals)) * 100


def _score(fn, series: dict[str, np.ndarray], origins: range | list[int]) -> tuple[float, float, int]:
    """Returns (model_wmape, naive_wmape, n_forecasts). Enforces the time budget."""
    m_errs, n_errs, acts = [], [], []
    n = 0
    t0 = time.perf_counter()
    for y in series.values():
        for o in origins:
            hist, actual = y[:o], float(y[o])
            if time.perf_counter() - t0 > BUDGET_SECONDS:
                raise TimeoutError(f"budget of {BUDGET_SECONDS}s exceeded after {n} forecasts")
            f = float(fn(hist))
            if not np.isfinite(f):
                raise ValueError(f"non-finite forecast at origin {o}")
            m_errs.append(f - actual)
            n_errs.append(float(hist[-1]) - actual)
            acts.append(actual)
            n += 1
    return _wmape(m_errs, acts), _wmape(n_errs, acts), n


def evaluate(fn) -> dict:
    full = prepare.generate_full()
    series = {s: g.sort_values("month").qty.to_numpy(dtype=float) for s, g in full.groupby("sku")}
    T, H = prepare.TRAIN_MONTHS, prepare.HOLDOUT_MONTHS

    dev_m, dev_n, n1 = _score(fn, series, range(T - DEV_H, T))
    hold_m, hold_n, n2 = _score(fn, series, range(T, T + H))

    return {
        "dev_wmape": round(dev_m, 2),
        "dev_fva": round(dev_n - dev_m, 2),
        "holdout_wmape": round(hold_m, 2),
        "holdout_fva": round(hold_n - hold_m, 2),
        "forecasts": n1 + n2,
    }


# ------------------------------------------------------------- references ---
def _ses(h: np.ndarray, a: float = 0.3) -> float:
    lvl = h[0]
    for x in h[1:]:
        lvl = a * x + (1 - a) * lvl
    return float(lvl)


def _seasonal_ses(h: np.ndarray) -> float:
    n, S = len(h), 12
    if n < 2 * S:
        return _ses(h)
    idx_m = np.arange(n) % S
    overall = h.mean() if h.mean() > 0 else 1.0
    idx = np.array([h[idx_m == m].mean() / overall if h[idx_m == m].mean() > 0 else 1.0 for m in range(S)])
    idx = np.where(idx <= 0, 1.0, idx)
    return float(max(0.0, _ses(h / idx[idx_m]) * idx[n % S]))


REFERENCES = {
    "ref: naive": lambda h: float(h[-1]),
    "ref: seasonal naive": lambda h: float(h[-12]) if len(h) >= 12 else float(h[-1]),
    "ref: 3-month MA": lambda h: float(h[-3:].mean()),
    "ref: SES(0.3)": _ses,
    "ref: seasonal SES": _seasonal_ses,
}


# ------------------------------------------------------------ leaderboard ---
def append_row(label: str, model_hash: str, res: dict, note: str) -> None:
    row = {
        "run_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "label": label,
        "model_sha": model_hash,
        "protocol_sha": protocol_hash(),
        **res,
        "note": note,
    }
    df = pd.DataFrame([row])
    header = not os.path.exists(LEADERBOARD_CSV)
    df.to_csv(LEADERBOARD_CSV, mode="a", index=False, header=header)
    render_md()


def render_md() -> None:
    if not os.path.exists(LEADERBOARD_CSV):
        return
    df = pd.read_csv(LEADERBOARD_CSV)
    cur = protocol_hash()
    df["⚑"] = np.where(df.protocol_sha != cur, "≠proto", "")
    best = df[df.protocol_sha == cur].holdout_fva.max()
    lines = [
        "# Leaderboard",
        "",
        f"Single metric: **FVA vs naive (WMAPE points; higher is better)**. "
        f"Best holdout FVA so far: **{best:+.2f}**. Protocol `{cur}`.",
        "",
        df.sort_values("holdout_fva", ascending=False)
        .loc[:, ["run_at_utc", "label", "dev_fva", "holdout_fva", "forecasts", "model_sha", "⚑", "note"]]
        .to_markdown(index=False),
        "",
        "*dev = agent-visible validation (last 6 train months); holdout = sealed final 6 months. "
        "A big dev/holdout gap is overfitting made visible.*",
    ]
    with open(LEADERBOARD_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def render_chart() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    df = pd.read_csv(LEADERBOARD_CSV)
    df = df[df.protocol_sha == protocol_hash()].reset_index(drop=True)
    agent = df[~df.label.str.startswith("ref:")]
    refs = df[df.label.str.startswith("ref:")]

    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    if len(agent):
        ax.plot(range(1, len(agent) + 1), agent.holdout_fva, color="#2a78d6", marker="o",
                linewidth=2, zorder=3, label="agent runs (holdout FVA)")
        ax.plot(range(1, len(agent) + 1), agent.dev_fva, color="#86b6ef", marker="o",
                linewidth=1.4, linestyle="--", zorder=2, label="agent runs (dev FVA)")
    for _, r in refs.iterrows():
        ax.axhline(r.holdout_fva, color="#c3c2b7", linewidth=1, linestyle=":")
        ax.text(0.35, r.holdout_fva + 0.12, r.label.replace("ref: ", ""), fontsize=8.5, color="#898781")
    ax.axhline(0, color="#52514e", linewidth=1.2)
    ax.set_xlabel("experiment #")
    ax.set_ylabel("FVA vs naive (WMAPE pts)")
    ax.set_title("Can an agent honestly beat naive forecasting?", loc="left", fontsize=13)
    ax.spines[["top", "right"]].set_visible(False)
    if len(agent):
        ax.legend(loc="lower right", frameon=False, fontsize=9)
    os.makedirs("charts", exist_ok=True)
    fig.tight_layout()
    fig.savefig("charts/leaderboard.svg")
    print("charts/leaderboard.svg written")


# ------------------------------------------------------------------ main ----
def load_model():
    spec = importlib.util.spec_from_file_location("model", "model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not callable(getattr(mod, "forecast_one", None)):
        sys.exit("model.py must define forecast_one(history) -> float")
    return mod.forecast_one


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--note", default="", help="one-line description of the experiment")
    ap.add_argument("--reference", action="store_true", help="score the built-in reference models")
    ap.add_argument("--chart", action="store_true", help="only redraw the leaderboard chart")
    args = ap.parse_args()

    if args.chart:
        render_chart()
        return

    if args.reference:
        for name, fn in REFERENCES.items():
            res = evaluate(fn)
            append_row(name, "-", res, "reference model")
            print(f"{name:22s} dev FVA {res['dev_fva']:+6.2f} | holdout FVA {res['holdout_fva']:+6.2f}")
        render_chart()
        return

    fn = load_model()
    res = evaluate(fn)
    append_row("agent", _sha("model.py")[:12], res, args.note)
    render_chart()
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
