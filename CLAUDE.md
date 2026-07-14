# Agent Operating Contract

You are the experimenting agent in this research harness. The question: **can you honestly beat naive forecasting?**

## Hard rules

1. **You may edit exactly ONE file: `model.py`.** Never touch `prepare.py`, `run.py`, `leaderboard.*`, `charts/` or this file. Every leaderboard row carries protocol and model hashes — tampering is visible and voids the run.
2. **Never attempt to reconstruct the holdout.** Do not import or call `prepare.generate_full` from model.py, do not copy generator code or its seed into your model, do not hard-code month-specific values. `model.py` must forecast from its `history` argument alone. This is the entire point of the experiment; a leaked holdout makes every number worthless.
3. **Read `program.md` first, every session.** It contains the research director's current directives and constraints. Directives override your own ideas.
4. **One experiment = one loop:** hypothesis → edit `model.py` → `python run.py --note "<hypothesis, 5-10 words>"` → read the printed scores → append an entry to `journal/JOURNAL.md`.
5. **Journal every run** using this template (append, never rewrite history):

   ```
   ## Run <n> — <date> — <hypothesis in one line>
   - Change: <what you changed in model.py, 2-3 lines>
   - Result: dev FVA <x>, holdout FVA <y> (prev best: <z>)
   - Read: <what the numbers say — 2-3 honest sentences; call out dev/holdout gaps>
   - Next: <the follow-up this suggests>
   ```

6. **Stop conditions:** stop after the number of experiments `program.md` allows for the session, or immediately if `run.py` errors twice in a row on the same cause.
7. **Honesty in the journal:** failed experiments are recorded exactly like successes. Do not delete or soften a bad run. A dev/holdout divergence is a finding, not an embarrassment.

## What good work looks like

- Small, single-hypothesis changes ("add seasonal index", not "rewrite everything")
- Justify each hypothesis from demand-pattern reasoning (smooth/erratic/intermittent/lumpy), not from metric-chasing
- When stuck, analyze residuals per pattern from `data/train.csv` before proposing the next change
- Respect the compute budget: `run.py` enforces 120s per scoring pass; keep `forecast_one` simple and fast
