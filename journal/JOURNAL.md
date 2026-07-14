# Experiment Journal

Every run — success or failure — is recorded here by the experimenting agent, using the template in [CLAUDE.md](../CLAUDE.md). The director's standing questions live in [program.md](../program.md).

---

## Run 1 — 2026-07-14 — seasonal-index baseline (directive step 1)
- Change: deseasonalize with per-month multiplicative indices, SES(0.3) on the deseasonalized level, reseasonalize with next month's index.
- Result: dev FVA **+3.98**, holdout FVA **+6.79** (prev best: — ; reference bar: +6.79)
- Read: replicates the seasonal-SES reference exactly — a sanity anchor proving the harness and my implementation agree. Answers the director's first standing question: seasonality alone recovers ~+6.8 of naive's disadvantage on holdout. Dev/holdout gap is −2.8 in the GOOD direction (holdout richer in seasonality than the dev window) — noted, not alarming per program.md rule 5 (the rule targets dev >> holdout).
- Next: directive step 2 — damped trend on the deseasonalized level (Holt with φ<1).

## Method caveat (standing)
- Holdout FVA is visible after each run; with 5 runs per session there is mild selection risk across experiments. The final write-up must report ALL runs, not the best one.
