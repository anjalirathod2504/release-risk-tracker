# Release Review — R6

## Gate decision: **CONDITIONAL GO**

| check                                 |   actual |   threshold | result   |
|:--------------------------------------|---------:|------------:|:---------|
| Open high-exposure risks (score ≥ 15) |        2 |           0 | FAIL     |
| Open S1 defects                       |        0 |           0 | PASS     |
| Open S2 defects                       |        2 |           3 | PASS     |
| Risks without an owner                |        0 |           0 | PASS     |

## Open risk register

| risk_id   | title                                   | category   | owner    | status     |   probability |   impact |   score | rating   |
|:----------|:----------------------------------------|:-----------|:---------|:-----------|--------------:|---------:|--------:|:---------|
| RK-029    | Performance regression in nightly build | Dependency | eng_lead | Open       |             5 |        3 |      15 | High     |
| RK-031    | Upgrade path untested on older OS       | Resource   | ops_lead | Mitigating |             5 |        3 |      15 | High     |
| RK-027    | Key engineer on leave during freeze     | Technical  | ops_lead | Open       |             3 |        4 |      12 | Medium   |
| RK-028    | Key engineer on leave during freeze     | Dependency | pm       | Open       |             5 |        2 |      10 | Medium   |
| RK-032    | Upgrade path untested on older OS       | Dependency | ops_lead | Open       |             3 |        3 |       9 | Medium   |
| RK-030    | Test lab capacity shortfall             | Schedule   | qa_lead  | Mitigating |             3 |        3 |       9 | Medium   |

![Risk heat map](risk_heatmap.png)

## Defect trend

User-reported defects: baseline avg 33.3 → latest 9 (-73.0%).

![Defect trend](defect_trend.png)

| release_id   | planned_date   |   total_defects |   user_reported |   high_severity |   still_open |   avg_days_to_close |
|:-------------|:---------------|----------------:|----------------:|----------------:|-------------:|--------------------:|
| R1           | 2025-01-15     |              82 |              32 |              23 |            0 |                11.2 |
| R2           | 2025-04-16     |              86 |              30 |              18 |            0 |                 9.8 |
| R3           | 2025-07-16     |              82 |              38 |              20 |            0 |                11.2 |
| R4           | 2025-10-15     |              66 |              20 |              26 |            0 |                11.6 |
| R5           | 2026-01-14     |              65 |              15 |              16 |            0 |                10.2 |
| R6           | 2026-04-15     |              56 |               9 |               8 |           21 |                10.8 |

## Component hotspots (user-reported)

| component   |   user_reported_defects |   high_severity |
|:------------|------------------------:|----------------:|
| Installer   |                      45 |               9 |
| Telemetry   |                      27 |              13 |
| Driver UI   |                      25 |               3 |
| Settings    |                      17 |               4 |
| Logging     |                      16 |               5 |
