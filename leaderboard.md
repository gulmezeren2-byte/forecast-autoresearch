# Leaderboard

Single metric: **FVA vs naive (WMAPE points; higher is better)**. Best holdout FVA so far: **+7.62**. Protocol `13e6b1b0e0e6`.

| run_at_utc       | label               |   dev_fva |   holdout_fva |   forecasts | model_sha    | ⚑   | note                                                         |
|:-----------------|:--------------------|----------:|--------------:|------------:|:-------------|:----|:-------------------------------------------------------------|
| 2026-07-14 10:57 | agent               |      4.29 |          7.62 |         288 | 16cc55f52ddd |     | pattern split: zero-share>0.2 -> 12m mean; else seasonal SES |
| 2026-07-14 10:57 | agent               |      4.62 |          7.57 |         288 | 8c9b041be777 |     | CV-shrunk seasonal indices on smooth branch                  |
| 2026-07-14 10:58 | agent               |      3.96 |          7.35 |         288 | 142ca7380b43 |     | intermittent branch: full-history mean (max restraint)       |
| 2026-07-14 11:02 | agent               |      4.01 |          7.2  |         288 | 96751f91f6bf |     | C2: Croston(0.15) on intermittent branch                     |
| 2026-07-14 10:55 | agent               |      3.98 |          6.79 |         288 | f9d824492c8e |     | seasonal index + SES on deseasonalized level                 |
| 2026-07-14 10:44 | ref: seasonal SES   |      3.98 |          6.79 |         288 | -            |     | reference model                                              |
| 2026-07-14 10:56 | agent               |      3.79 |          6.38 |         288 | 92e0ffb37c12 |     | damped-trend Holt on deseasonalized level (phi=0.85)         |
| 2026-07-14 10:44 | ref: seasonal naive |     -0.94 |          3.56 |         288 | -            |     | reference model                                              |
| 2026-07-14 10:44 | ref: SES(0.3)       |      1.2  |          3.3  |         288 | -            |     | reference model                                              |
| 2026-07-14 10:44 | ref: 3-month MA     |      1.38 |          2.07 |         288 | -            |     | reference model                                              |
| 2026-07-14 10:44 | ref: naive          |      0    |          0    |         288 | -            |     | reference model                                              |

*dev = agent-visible validation (last 6 train months); holdout = sealed final 6 months. A big dev/holdout gap is overfitting made visible.*
