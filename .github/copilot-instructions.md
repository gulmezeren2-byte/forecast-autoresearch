# Copilot instructions — forecast-autoresearch

A sealed-holdout forecasting experiment harness where an AI agent edits a single file (`model.py`) to honestly beat a naive baseline, judged by **FVA = naive WMAPE − model WMAPE** (points) on a 6-month holdout that is never written to disk.

## Build, test, run

```bash
pip install -r requirements.txt    # numpy, pandas, matplotlib, tabulate
python prepare.py                  # regenerate data/train.csv (seeded, deterministic)
python run.py --reference          # rebuild the reference bar (seasonal SES = +6.79 holdout)
python -m pytest tests/ -q         # protocol determinism tests (exactly what CI runs)
python run.py --note "hypothesis"  # score current model.py, append leaderboard + redraw chart
```

CI (`.github/workflows/ci.yml`) runs only the pytest step on Python 3.12; code targets 3.10+.

## Architecture

- `prepare.py` — **frozen.** Generates 24 SKUs × 48 months over four demand patterns (smooth/erratic/intermittent/lumpy) from `SEED`; writes the first 42 months to `data/train.csv`. The final 6 months (holdout) are never materialized — `run.py` regenerates them in memory at scoring time.
- `model.py` — **the only agent-editable file.** Implement `forecast_one(history) -> float`: `history` is a 1-D numpy array (oldest-first, ≥12 values) for one SKU; return next month's forecast. Must be deterministic and read no files.
- `run.py` — **frozen judge.** Scores dev (rolling origin over the last 6 train months) and holdout; enforces a 120s wall-clock budget; hashes `prepare.py|run.py` + `model.py` into every leaderboard row; writes `leaderboard.csv/.md` and `charts/leaderboard.svg`.
- `program.md` — human-only research directives (budget, scope, sequence, stop rules). `CLAUDE.md` — the agent operating contract. `journal/JOURNAL.md` — append-only per-run log.

## Conventions

- **Edit only `model.py`.** Never modify `prepare.py`, `run.py`, `program.md`, `leaderboard.*`, `charts/`, or `CLAUDE.md` — recorded hashes make tampering visible and void the run.
- **Never reconstruct the holdout:** do not import/call `prepare.generate_full`, copy generator code or the seed, or hard-code month-specific values. Forecast from the `history` argument alone.
- **Read `program.md` first every session;** its directives override your own ideas (current scope: numpy + stdlib only in `model.py`, ≤3 components, per-series tuning only against a series' own in-history one-step errors — never against dev scores).
- **One experiment = one loop:** hypothesis -> edit `model.py` -> `python run.py --note "<5–10 words>"` -> read printed scores -> append a `journal/JOURNAL.md` entry (append-only; log failures exactly like successes).
- **Refuse dev-only gains:** a change that improves dev but not holdout is rejected (standing principle). Keep `forecast_one` simple and fast — 120s covers all forecast calls per scoring pass.
