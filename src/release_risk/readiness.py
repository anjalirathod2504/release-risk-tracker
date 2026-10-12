"""Release readiness gate: turns the risk register and defect data into a Go / No-Go call.

The rules are deliberately simple and explicit, so a release review can debate
the thresholds rather than the arithmetic. Change them in GateRules.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class GateRules:
    max_open_high_risks: int = 0           # risks with score >= 15 must be mitigated/closed
    max_open_s1: int = 0                   # no open S1 defects
    max_open_s2: int = 3
    max_unowned_risks: int = 0


@dataclass
class GateResult:
    release_id: str
    decision: str
    checks: list[dict] = field(default_factory=list)

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.checks)


def evaluate(release_id: str, risks: pd.DataFrame, defects: pd.DataFrame,
             rules: GateRules | None = None) -> GateResult:
    rules = rules or GateRules()
    r = risks[(risks["release_id"] == release_id) & (risks["status"] != "Closed")].copy()
    r["score"] = r["probability"] * r["impact"]
    d = defects[(defects["release_id"] == release_id) & defects["closed_on"].isna()]

    checks = [
        ("Open high-exposure risks (score ≥ 15)", int((r["score"] >= 15).sum()), rules.max_open_high_risks),
        ("Open S1 defects", int((d["severity"] == "S1").sum()), rules.max_open_s1),
        ("Open S2 defects", int((d["severity"] == "S2").sum()), rules.max_open_s2),
        ("Risks without an owner", int(r["owner"].isna().sum()), rules.max_unowned_risks),
    ]
    rows = [{"check": name, "actual": actual, "threshold": limit,
             "result": "PASS" if actual <= limit else "FAIL"} for name, actual, limit in checks]
    fails = sum(row["result"] == "FAIL" for row in rows)
    decision = "GO" if fails == 0 else "CONDITIONAL GO" if fails == 1 else "NO-GO"
    return GateResult(release_id, decision, rows)


def defect_trend(by_release: pd.DataFrame, baseline_releases: int = 3) -> dict[str, float]:
    """Compare average user-reported defects in the latest release to the baseline average."""
    base = by_release.head(baseline_releases)["user_reported"].mean()
    latest = by_release.iloc[-1]["user_reported"]
    return {"baseline_avg": round(float(base), 1), "latest": int(latest),
            "change_pct": round((latest - base) / base * 100, 1)}
