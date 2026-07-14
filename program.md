# Research Program

*This file is edited by the research director (Eren Gülmez) — never by the agent. It is the experiment's steering wheel: the agent reads it at the start of every session and follows it over its own preferences.*

## Current directives — cycle 1

1. **Budget:** maximum 5 experiments per session.
2. **Scope:** classical statistics only — smoothing, seasonal decomposition, trend damping, simple combinations. No ML libraries, no external data, standard library + numpy only.
3. **Sequence to explore first:**
   - establish a seasonal-index baseline (deseasonalize → smooth → reseasonalize)
   - then test trend damping on top
   - then a pattern-aware split: intermittent/lumpy SKUs may deserve a different rule (e.g., long-window mean) than smooth ones — decide from train-set residuals, justify in the journal
4. **Forbidden:** anything that touches rule 2 of CLAUDE.md (holdout reconstruction); per-month hard-coded values; ensembles of more than 3 components (interpretability matters).
5. **Reporting bar:** every journal entry must state the dev/holdout gap explicitly. If holdout FVA lags dev FVA by more than 1.5 points for two consecutive runs, stop and write a diagnosis instead of a fifth experiment.

## Standing questions the director wants answered

- How much of naive's disadvantage is purely seasonality?
- Is there ANY honest monthly method that helps lumpy SKUs, or is the correct answer "stop forecasting these, buffer them" (as the [abc-xyz study](https://github.com/gulmezeren2-byte/abc-xyz-inventory) suggests)?
- Where does the marginal experiment stop paying? (The answer is a finding for practice, not a failure.)

## Directive history

- 2026-07-14 — cycle 1 opened: classical-statistics scope, 5-experiment sessions.
- 2026-07-14 — cycle 1 closed: bar cleared at +7.62 (run 3, pattern-aware split). Findings and refused changes in journal/JOURNAL.md. Cycle 2 scope to be decided by the director — candidate directions: Croston-style intermittent methods, dev-window redesign (rolling 12 instead of last 6), per-pattern error reporting in run.py (would require a protocol version bump).
