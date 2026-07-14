# Leaderboard

Single metric: **FVA vs naive (WMAPE points; higher is better)**. Best holdout FVA so far: **+6.79**. Protocol `13e6b1b0e0e6`.

| run_at_utc       | label               |   dev_fva |   holdout_fva |   forecasts | model_sha    | ⚑   | note                                         |
|:-----------------|:--------------------|----------:|--------------:|------------:|:-------------|:----|:---------------------------------------------|
| 2026-07-14 10:44 | ref: seasonal SES   |      3.98 |          6.79 |         288 | -            |     | reference model                              |
| 2026-07-14 10:55 | agent               |      3.98 |          6.79 |         288 | f9d824492c8e |     | seasonal index + SES on deseasonalized level |
| 2026-07-14 10:44 | ref: seasonal naive |     -0.94 |          3.56 |         288 | -            |     | reference model                              |
| 2026-07-14 10:44 | ref: SES(0.3)       |      1.2  |          3.3  |         288 | -            |     | reference model                              |
| 2026-07-14 10:44 | ref: 3-month MA     |      1.38 |          2.07 |         288 | -            |     | reference model                              |
| 2026-07-14 10:44 | ref: naive          |      0    |          0    |         288 | -            |     | reference model                              |

*dev = agent-visible validation (last 6 train months); holdout = sealed final 6 months. A big dev/holdout gap is overfitting made visible.*
