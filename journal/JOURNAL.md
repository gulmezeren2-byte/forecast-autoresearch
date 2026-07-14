# Experiment Journal

Every run — success or failure — is recorded here by the experimenting agent, using the template in [CLAUDE.md](../CLAUDE.md). The director's standing questions live in [program.md](../program.md).

---

## Run 1 — 2026-07-14 — seasonal-index baseline (directive step 1)
- Change: deseasonalize with per-month multiplicative indices, SES(0.3) on the deseasonalized level, reseasonalize with next month's index.
- Result: dev FVA **+3.98**, holdout FVA **+6.79** (prev best: — ; reference bar: +6.79)
- Read: replicates the seasonal-SES reference exactly — a sanity anchor proving the harness and my implementation agree. Answers the director's first standing question: seasonality alone recovers ~+6.8 of naive's disadvantage on holdout. Dev/holdout gap is −2.8 in the GOOD direction (holdout richer in seasonality than the dev window) — noted, not alarming per program.md rule 5 (the rule targets dev >> holdout).
- Next: directive step 2 — damped trend on the deseasonalized level (Holt with φ<1).

## Run 2 — 2026-07-14 — damped trend on the deseasonalized level (directive step 2)
- Change: replaced SES with Holt level+trend (α=0.3, β=0.1) and damping φ=0.85 on the deseasonalized series.
- Result: dev FVA **+3.79**, holdout FVA **+6.38** (prev best: +6.79)
- Read: worse on BOTH windows (−0.19 dev, −0.41 holdout). After deseasonalizing, the generator's mild trends are apparently absorbed well enough by SES's level; explicit trend machinery reacts to noise. Consistent conclusion, not window luck. Damped trend is retired for this universe.
- Next: directive step 3 — pattern-aware split. Justification from train.csv: 10 of 24 SKUs have >20% zero months; for those, each per-month seasonal index rests on ~3-4 observations, so the index mostly amplifies noise. Hypothesis: a plain 12-month mean is a calmer estimator for intermittent/lumpy SKUs; keep run-1 logic for smooth ones.

## Run 3 — 2026-07-14 — pattern-aware split (directive step 3) — **BAR CLEARED**
- Change: SKUs with >20% zero months get a plain 12-month mean; the rest keep run-1 seasonal SES. Detection is from the history argument alone (no labels used).
- Result: dev FVA **+4.29**, holdout FVA **+7.62** (prev best +6.79 — reference bar CLEARED by +0.83)
- Read: the single biggest gain of the cycle, and it came from *restraint*: per-month indices on intermittent series rest on 3-4 observations and mostly amplify noise; replacing them with a calm mean helped both windows (dev +0.31, holdout +0.83 vs run 1). This is the abc-xyz thesis showing up inside a forecasting model: volatile demand rewards buffering-style calmness, not pattern-chasing. Dev/holdout moved together — no overfitting signal.
- Next: directive step 3's second idea — the erratic (nonzero but high-noise) SKUs also get spurious seasonal indices; try shrinking indices toward 1 in proportion to noise (CV-based), smooth branch only.

## Run 4 — 2026-07-14 — CV-shrunk seasonal indices
- Change: on the seasonal branch, indices shrunk toward 1 by k = 1/(1+max(0, cv−0.3)).
- Result: dev FVA **+4.62**, holdout FVA **+7.57** (prev best +7.62)
- Read: dev up +0.33, holdout down −0.05 — the textbook marginal-overfit signature: the tweak fits the dev window's erratic mix and does not generalize. The −0.05 is within noise, but when a change helps only the window I can iterate on, the honest default is to refuse it. Per program.md's interpretability rule, shrinkage is dropped and run 3 stands as the base.
- Next: final experiment of the session — push run 3's actual lesson (restraint on volatile series) further: intermittent branch moves from a 12-month mean to the full-history mean.

## Run 5 — 2026-07-14 — full-history mean on the intermittent branch
- Change: intermittent/lumpy branch moved from last-12-months mean to full-history mean.
- Result: dev FVA **+3.96**, holdout FVA **+7.35** (prev best +7.62)
- Read: worse on both windows (−0.33 dev, −0.27 holdout vs run 3) — consistent, so a real effect: maximum restraint overshoots. The intermittent series drift slowly; a 12-month window balances calmness with adaptivity. Restraint is a dial, not a direction.
- Next: session budget (5 experiments) reached — cycle closed.

## Cycle 1 summary — 2026-07-14

**Question:** can the agent honestly beat naive? **Answer: yes — holdout FVA +7.62 (bar was +6.79), reached at run 3 of 5.**

| Run | Idea | Dev FVA | Holdout FVA |
|-----|------|--------:|------------:|
| 1 | seasonal index + SES | +3.98 | +6.79 |
| 2 | + damped trend | +3.79 | +6.38 |
| **3** | **pattern split: zero-share>0.2 → 12m mean** | **+4.29** | **+7.62** |
| 4 | + CV-shrunk indices | +4.62 | +7.57 |
| 5 | full-history mean on split branch | +3.96 | +7.35 |

Final model of record: **run 3** (model.py reverted to it; its hash matches leaderboard row 3).

**What the cycle actually taught:**
1. Seasonality is the whole naive gap on smooth demand (+6.8 of it) — run 1.
2. Trend machinery on deseasonalized monthly retail-like demand is noise-chasing — run 2.
3. The winning move was *restraint*: refusing to fit seasonal indices to intermittent series. The director's abc-xyz thesis, reproduced inside a forecasting model — run 3.
4. A change that improves only the window you iterate on must be refused — run 4, declined on principle.
5. Restraint has an optimum; more of it is not better — run 5.

Director's standing question 2 ("is there ANY honest monthly method that helps lumpy SKUs?") — partial answer: yes, but the helpful move is *calmer estimation*, not better pattern detection. The practical ceiling for these SKUs remains low; buffering advice stands.

## Run 6 — 2026-07-14 — cycle 2 opens: Croston(α=0.15) on the intermittent branch
- Change: intermittent branch's 12-month mean replaced by classic Croston (separate SES of nonzero sizes and inter-demand intervals).
- Result: dev FVA **+4.01**, holdout FVA **+7.20** (champion: +4.29 / +7.62)
- Read: worse on both windows — a real, consistent loss, not window luck. Diagnosis: these intermittent series have near-stationary occurrence; Croston earns its keep when demand *intervals drift*, which this universe lacks. Against a stationary process, the 12-month mean is already close to the Bayes answer and Croston's recency-weighting only adds variance.
- Next: directive step 2 — SBA bias correction (×(1−α/2)). Croston runs hot by construction; the correction may recover part of the loss. Warning flag: if this also lands below champion, stop rule 6 (two consecutive holdout regressions) triggers.

## Run 7 — 2026-07-14 — Croston + SBA correction
- Change: SBA factor (1−α/2) on the Croston rate.
- Result: dev FVA **+4.07**, holdout FVA **+7.31** (champion still +7.62)
- Read: the correction recovers part of Croston's bias (+0.11 holdout vs run 6) but the family still loses to the plain 12-month mean on both windows. Verdict per directive step 2: holdout supports the mean — Croston/SBA measured and retired for this universe. Note the asymmetry with textbooks: Croston is the *literature's* answer for intermittent demand, but its edge assumes drifting intervals; against stationary occurrence, calm wins. That is itself a publishable finding.
- Next: directive step 3 — per-series α for the smooth branch's SES, tuned only against each series' own in-history one-step errors (grid 0.1–0.5). Intermittent branch reverts to the champion's 12-month mean.

## Run 8 — 2026-07-14 — per-series α (in-history tuning) — **NEW CHAMPION +8.01**
- Change: intermittent branch back to the 12-month mean; smooth branch's SES α chosen per series from {0.1..0.5} by one-step error over the series' own deseasonalized history.
- Result: dev FVA **+4.19**, holdout FVA **+8.01** (prev champion +7.62 → +0.39)
- Read: the win generalizes precisely because the tuning never saw the dev window — each series picks the responsiveness its own history justifies. Dev moved little (−0.10 vs run 3) while holdout jumped: the opposite signature of run 4's refused change, and the cleanest evidence yet that in-history tuning is the legitimate way to add flexibility.
- Next: directive step 4 — median-based seasonal indices on the smooth branch (robust to single-month outliers).

## Run 9 — 2026-07-14 — median-based seasonal indices
- Change: per-month indices from medians (and median normalization) instead of means.
- Result: dev FVA **+2.73**, holdout FVA **+5.95** (champion +8.01)
- Read: a large, consistent regression on both windows. With only 3-4 observations per month-slot, a median is a coarser estimator than the mean, and median normalization distorts the level for skewed series. "Robust" is not free — robustness pays when outliers exist; this universe's smooth series don't have enough of them to cover the efficiency loss. Reverted.
- Next: final slot (agent's discretion). Chosen: generalize run 8's *legitimate* mechanism — in-history selection — to the intermittent branch: choose the mean window per series from {6, 12, 24, all} by one-step error over the series' own history.

## Run 10 — 2026-07-14 — in-history window selection on the intermittent branch — **CHAMPION +8.13**
- Change: run 8 kept; the intermittent branch's mean window chosen per series from {6, 12, 24, all} by one-step error over the series' own last year of history.
- Result: dev FVA **+4.33**, holdout FVA **+8.13** (prev champion +8.01)
- Read: both windows improved — the same signature as run 8 and for the same reason: the flexibility was earned from each series' own past, not from the evaluation window. The mechanism, not any single model, is the discovery of this cycle.
- Next: session budget reached — cycle closed.

## Cycle 2 summary — 2026-07-14

**Champion: run 10, holdout FVA +8.13** (cycle 1 left off at +7.62; bar was +6.79).

| Run | Idea | Dev FVA | Holdout FVA |
|-----|------|--------:|------------:|
| 6 | Croston(0.15) on intermittent | +4.01 | +7.20 |
| 7 | + SBA correction | +4.07 | +7.31 |
| **8** | per-series α (in-history) | +4.19 | **+8.01** |
| 9 | median seasonal indices | +2.73 | +5.95 |
| **10** | + in-history window choice for intermittent | **+4.33** | **+8.13** |

**What cycle 2 taught:**
1. **The textbook's specialist lost.** Croston — the literature's answer for intermittent demand — measured below a plain 12-month mean here (runs 6-7). Its edge assumes drifting demand intervals; against stationary occurrence, calm wins. Method choice must follow the data's actual failure mode, not the method's reputation.
2. **The cycle's real discovery is a mechanism, not a model:** in-history self-tuning (each series choosing its α, its window, from its own past) improved holdout twice, on both branches (runs 8, 10) — while every form of *imposed* cleverness (trend, shrinkage, medians, Croston) lost.
3. **"Robust" is not free** (run 9): with 3-4 observations per seasonal slot, medians throw away efficiency the outliers never threatened.
4. Two cycles, ten experiments, four refusals/regressions fully logged. The final model remains ~15 lines of interpretable numpy.

## Method caveat (standing)
- Holdout FVA is visible after each run; with 5 runs per session there is mild selection risk across experiments. The final write-up must report ALL runs, not the best one.
