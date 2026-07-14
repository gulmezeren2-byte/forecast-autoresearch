# Forecast Autoresearch — can an AI agent honestly beat naive forecasting?

[![CI](https://github.com/gulmezeren2-byte/forecast-autoresearch/actions/workflows/ci.yml/badge.svg)](https://github.com/gulmezeren2-byte/forecast-autoresearch/actions/workflows/ci.yml) ![Python](https://img.shields.io/badge/python-3.10+-blue) ![License](https://img.shields.io/badge/license-MIT-green)

🇹🇷 Türkçesi: [README.tr.md](README.tr.md)

> An AI agent gets **one file to edit**, a **sealed holdout it can never see**, a fixed experiment budget, and a single honest metric: **value added over shipping last month's number**.
> The bar set by classical statistics: **+6.79 points**. Two cycles and ten experiments later: **+8.13.**

![Leaderboard](charts/leaderboard.svg)

**Status — cycles 1-2 complete (10 experiments, 4 refusals/regressions fully logged):** the bar fell to *restraint* (refusing seasonal indices on intermittent demand), then the record fell twice to one legitimate mechanism — **in-history self-tuning**: each series choosing its own smoothing and window from its own past, never from the evaluation window. The textbook's specialist for intermittent demand (Croston/SBA) was measured and lost to a plain mean; "robust" medians regressed hard; a dev-only gain was refused on principle. Every run is on the [leaderboard](leaderboard.md) and in the [journal](journal/JOURNAL.md), with the reasoning.

## The reference bar (real numbers, frozen protocol)

| Model | Dev FVA | **Holdout FVA** |
|-------|--------:|----------------:|
| naive (last month) | +0.00 | +0.00 |
| seasonal naive | −0.94 | +3.56 |
| 3-month moving average | +1.38 | +2.07 |
| SES (α=0.3) | +1.20 | +3.30 |
| **seasonal SES** | **+3.98** | **+6.79** |

Already one finding before any agent touched anything: seasonal naive *loses* to naive on the dev window and *wins* by +3.56 on the holdout — window choice alone can flip a model comparison. This is exactly the kind of thing single-split evaluations hide.

## The protocol (frozen)

- **One editable file.** The agent may modify `model.py` and nothing else — a single function, `forecast_one(history) -> float`.
- **A sealed holdout.** The final 6 months are never written to disk; `run.py` regenerates them in memory from the seed at scoring time. The agent iterates against a *dev* window (last 6 training months) and is judged on the holdout it cannot inspect.
- **One metric.** FVA = naive WMAPE − model WMAPE, in points. Positive means the work added value over doing nothing; the [forecast-accuracy-lab](https://github.com/gulmezeren2-byte/forecast-accuracy-lab) discipline, applied to an agent.
- **A budget.** 120 seconds of wall-clock per scoring pass — elegance over brute force.
- **Tamper evidence.** Every leaderboard row records hashes of the protocol files and of `model.py`. Guardrails are procedural and auditable (git history + hashes), and the operating rules in [CLAUDE.md](CLAUDE.md) forbid holdout reconstruction explicitly.

## The division of labor is the experiment

| File | Edited by | Role |
|------|-----------|------|
| [`prepare.py`](prepare.py) | nobody (frozen) | The world: 24 SKUs × 48 months across smooth/erratic/intermittent/lumpy demand |
| [`model.py`](model.py) | **the agent** | The only lever: one forecasting function, starting at naive (FVA = 0.0) |
| [`program.md`](program.md) | **the human** | The research directives: scope, budget, sequence, forbidden moves, stop rules |
| [`run.py`](run.py) | nobody (frozen) | The judge: scores, enforces budget, writes the leaderboard and chart |

The human never writes the model; the agent never sets the agenda. `program.md` is the steering wheel — read it to see how the research is being directed.

## Run it yourself

```bash
git clone https://github.com/gulmezeren2-byte/forecast-autoresearch && cd forecast-autoresearch
pip install -r requirements.txt
python prepare.py           # regenerate the training data (seeded)
python run.py --reference   # rebuild the reference bar — same numbers, every time
python -m pytest tests/ -q  # protocol determinism tests
```

To run your own experiment loop (human or agent): edit `model.py`, then `python run.py --note "your hypothesis"`.

## Why this exists

Everyone is asking what AI agents can automate. This repo asks a narrower, harder question from the *measurement honesty* series: **when self-deception is made impossible by protocol — sealed holdout, naive benchmark, budget, journal — how much forecasting value can an agent actually add?** Both outcomes are findings. If the agent clears +6.79, that is a documented, reproducible capability. If it plateaus, that is evidence for what [forecast-accuracy-lab](https://github.com/gulmezeren2-byte/forecast-accuracy-lab) and [abc-xyz-inventory](https://github.com/gulmezeren2-byte/abc-xyz-inventory) already argue: some demand should be buffered, not forecast — no matter who does the forecasting.

## Roadmap

- [ ] Experiment cycle 1: classical statistics scope (see `program.md`)
- [ ] Pattern-split directives: should lumpy SKUs get their own rule?
- [ ] Cycle write-up with the full journal
- [ ] Cycle 2: wider scope, if cycle 1 earns it

## 🇹🇷 Türkçe özet

Bir yapay zeka ajanına tek düzenlenebilir dosya, asla göremeyeceği mühürlü bir test dönemi, sabit deney bütçesi ve tek dürüst metrik veriliyor: naive'e karşı katma değer (FVA). Klasik istatistiğin koyduğu çıta: **+6,79 puan.** İnsan `program.md` ile araştırmayı yönetiyor, ajan yalnızca `model.py`'ı düzenliyor; her deney — başarılı ya da başarısız — skor tablosuna ve günlüğe işleniyor. Tam Türkçe sürüm: [README.tr.md](README.tr.md)

## About

Designed and directed by **[Eren Gülmez](https://www.linkedin.com/in/erengulmez)** — industrial engineer, İstanbul. The capstone experiment of my *measurement honesty* series: the human designs the measurement system and directs the research; the agent does the trying.

Part of an open industrial-engineering toolkit → **[awesome-industrial-engineering](https://github.com/gulmezeren2-byte/awesome-industrial-engineering)**

## License

[MIT](LICENSE)
