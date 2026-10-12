import pandas as pd

from release_risk import db, readiness, sample_data


def _db():
    con = db.connect()
    db.init_schema(con)
    db.load_frames(con, *sample_data.build())
    return con


def test_named_queries_parse():
    assert {"open_risks_by_score", "defects_by_release", "component_hotspots"} <= set(db.named_queries())


def test_risk_scores_sorted():
    reg = db.query(_db(), "open_risks_by_score")
    assert (reg["score"] == reg["probability"] * reg["impact"]).all()
    assert reg["score"].is_monotonic_decreasing


def test_gate_fails_on_open_s1():
    risks = pd.DataFrame([dict(release_id="X", status="Open", probability=1, impact=1, owner="pm")])
    defects = pd.DataFrame([dict(release_id="X", severity="S1", closed_on=None)])
    assert readiness.evaluate("X", risks, defects).decision == "CONDITIONAL GO"


def test_gate_go_when_clean():
    risks = pd.DataFrame([dict(release_id="X", status="Closed", probability=5, impact=5, owner="pm")])
    defects = pd.DataFrame([dict(release_id="X", severity="S1", closed_on="2026-01-01")])
    assert readiness.evaluate("X", risks, defects).decision == "GO"


def test_user_reported_defects_trend_down():
    trend = readiness.defect_trend(db.query(_db(), "defects_by_release"))
    assert trend["change_pct"] < 0
