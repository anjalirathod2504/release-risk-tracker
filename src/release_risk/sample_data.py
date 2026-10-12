"""Synthetic release, risk and defect data (no real company data).

Six quarterly releases. From R4 onward a data-driven triage process is applied
(hotspot components get extra test coverage), so user-reported defects fall.
"""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

COMPONENTS = ["Installer", "Driver UI", "Telemetry", "Update Service", "Settings", "Logging"]
CATEGORIES = ["Schedule", "Technical", "Resource", "Dependency", "Quality"]
OWNERS = ["eng_lead", "qa_lead", "ops_lead", "pm"]
RISK_TITLES = [
    "Vendor SDK drop may slip", "Test lab capacity shortfall", "Flaky regression suite",
    "Key engineer on leave during freeze", "Late requirement change from business",
    "Upgrade path untested on older OS", "Performance regression in nightly build",
    "Localization strings not final", "Security review not scheduled",
]


def build(seed: int = 7) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    releases, risks, defects = [], [], []
    start = date(2025, 1, 15)
    did = rid = 0
    for i in range(1, 7):
        rel_id = f"R{i}"
        planned = start + timedelta(days=91 * (i - 1))
        releases.append({"release_id": rel_id, "name": f"Release {i}", "planned_date": planned.isoformat(),
                         "status": "Released" if i < 6 else "In Progress"})
        # risks
        for _ in range(rng.integers(4, 8)):
            rid += 1
            closed = i < 6 and rng.random() < 0.85
            risks.append({
                "risk_id": f"RK-{rid:03d}", "release_id": rel_id,
                "title": str(rng.choice(RISK_TITLES)), "category": str(rng.choice(CATEGORIES)),
                "probability": int(rng.integers(1, 6)), "impact": int(rng.integers(1, 6)),
                "owner": str(rng.choice(OWNERS)),
                "status": "Closed" if closed else str(rng.choice(["Open", "Mitigating"])),
                "raised_on": (planned - timedelta(days=int(rng.integers(20, 80)))).isoformat(),
                "mitigation": None,
            })
        # defects: user-reported rate drops after R3
        n_internal = int(rng.integers(40, 60))
        n_user = int(rng.integers(30, 40)) if i <= 3 else int(rng.integers(30, 40) * (0.55 - 0.12 * (i - 4)))
        weights = np.array([3, 2, 2, 1, 1, 1], float)
        if i > 3:
            weights[[0, 1]] *= 0.4  # hotspots fixed
        weights /= weights.sum()
        for source, n in (("Internal QA", n_internal), ("User Reported", n_user)):
            for _ in range(n):
                did += 1
                opened = planned + timedelta(days=int(rng.integers(-60, 30)))
                closed_on = None
                if i < 6 or rng.random() < 0.5:
                    closed_on = (opened + timedelta(days=int(rng.integers(1, 21)))).isoformat()
                defects.append({
                    "defect_id": f"DF-{did:04d}", "release_id": rel_id,
                    "component": str(rng.choice(COMPONENTS, p=weights)),
                    "severity": str(rng.choice(["S1", "S2", "S3", "S4"], p=[.05, .2, .45, .3])),
                    "source": source, "opened_on": opened.isoformat(), "closed_on": closed_on,
                })
    return pd.DataFrame(releases), pd.DataFrame(risks), pd.DataFrame(defects)
