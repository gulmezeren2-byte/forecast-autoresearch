# Research Program

*This file is edited by the research director (Eren Gülmez) — never by the agent. It is the experiment's steering wheel: the agent reads it at the start of every session and follows it over its own preferences.*

## Current directives — cycle 2

1. **Budget:** maximum 5 experiments this session. Champion to beat: run 3, holdout FVA **+7.62**.
2. **Scope:** cycle-1 scope PLUS the intermittent-demand classics — Croston's method and its SBA bias correction. Per-series parameter tuning is allowed ONLY against the series' own in-history one-step errors (never against dev scores). Still numpy + stdlib only.
3. **Sequence to explore:**
   - Croston on the intermittent branch (replace the 12-month mean; α around 0.1–0.2)
   - SBA bias correction on top — keep whichever the holdout supports
   - per-series α tuning for the smooth branch's SES, tuned in-history only
   - robust (median-based) seasonal indices on the smooth branch
   - fifth slot at the agent's discretion, justified from train residuals
4. **Standing principle (from cycle 1, run 4):** a change that improves dev but not holdout is refused, whatever the dev gain.
5. **Forbidden:** unchanged (no holdout reconstruction, no per-month hard-coding, ≤3 components, no protocol edits).
6. **Stop rules:** cycle-1 rule stays; additionally, stop early if two consecutive experiments worsen holdout — do not dig.

## Standing questions the director wants answered

- How much of naive's disadvantage is purely seasonality?
- Is there ANY honest monthly method that helps lumpy SKUs, or is the correct answer "stop forecasting these, buffer them" (as the [abc-xyz study](https://github.com/gulmezeren2-byte/abc-xyz-inventory) suggests)?
- Where does the marginal experiment stop paying? (The answer is a finding for practice, not a failure.)

## Directive history

- 2026-07-14 — cycle 1 opened: classical-statistics scope, 5-experiment sessions.
- 2026-07-14 — cycle 1 closed: bar cleared at +7.62 (run 3, pattern-aware split). Findings and refused changes in journal/JOURNAL.md. Cycle 2 scope to be decided by the director — candidate directions: Croston-style intermittent methods, dev-window redesign (rolling 12 instead of last 6), per-pattern error reporting in run.py (would require a protocol version bump).
