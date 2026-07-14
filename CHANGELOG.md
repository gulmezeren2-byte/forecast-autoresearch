# Changelog

## [0.1.0] — 2026-07-14

### Added
- The frozen protocol: `prepare.py` (24 SKUs × 48 months, seeded; sealed 6-month holdout never materialized on disk) and `run.py` (dev/holdout FVA scoring, 120s budget, tamper-evident hashes, leaderboard + chart rendering)
- `model.py` — the agent's single editable file, starting at naive (FVA = 0.0)
- `program.md` — the research director's directives (cycle 1: classical statistics)
- `CLAUDE.md` — the agent operating contract (one-file rule, no holdout reconstruction, journal template, stop conditions)
- Reference bar scored and frozen: seasonal SES holdout FVA **+6.79**
- 5 protocol determinism tests, including a holdout-leak check
- Bilingual README (EN + TR)
