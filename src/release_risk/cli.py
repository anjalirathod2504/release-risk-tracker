"""Command-line entry point.

    python -m release_risk.cli build      # create data/release.db with sample data
    python -m release_risk.cli report     # write reports/release_review.md + charts
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from . import db, readiness, sample_data

DB_PATH = db.ROOT / "data" / "release.db"
REPORTS = db.ROOT / "reports"


def build() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    DB_PATH.unlink(missing_ok=True)
    con = db.connect(DB_PATH)
    db.init_schema(con)
    db.load_frames(con, *sample_data.build())
    print(f"Built {DB_PATH}")


def report() -> None:
    con = db.connect(DB_PATH)
    REPORTS.mkdir(exist_ok=True)
    risks_reg = db.query(con, "open_risks_by_score")
    by_rel = db.query(con, "defects_by_release")
    hot = db.query(con, "component_hotspots")
    risks = pd.read_sql_query("SELECT * FROM risks", con)
    defects = pd.read_sql_query("SELECT * FROM defects", con)
    current = pd.read_sql_query(
        "SELECT release_id FROM releases WHERE status <> 'Released' ORDER BY planned_date LIMIT 1", con
    )["release_id"].iloc[0]
    gate = readiness.evaluate(current, risks, defects)
    trend = readiness.defect_trend(by_rel)

    # Heat map of open risks
    fig, ax = plt.subplots(figsize=(4.2, 4))
    grid = [[0] * 5 for _ in range(5)]
    for _, row in risks_reg.iterrows():
        grid[row.impact - 1][row.probability - 1] += 1
    colors = [[(p * i) for p in range(1, 6)] for i in range(1, 6)]
    ax.imshow(colors, cmap="RdYlGn_r", origin="lower", alpha=0.75, extent=(0.5, 5.5, 0.5, 5.5))
    for i in range(5):
        for p in range(5):
            if grid[i][p]:
                ax.text(p + 1, i + 1, grid[i][p], ha="center", va="center", fontsize=11, weight="bold")
    ax.set_xlabel("Probability"); ax.set_ylabel("Impact"); ax.set_title("Open risk heat map", fontsize=10)
    fig.tight_layout(); fig.savefig(REPORTS / "risk_heatmap.png", dpi=150); plt.close(fig)

    # Defect trend
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(by_rel["release_id"], by_rel["user_reported"], marker="o", color="#e76f51", label="User reported")
    ax.plot(by_rel["release_id"], by_rel["total_defects"] - by_rel["user_reported"], marker="o",
            color="#2a9d8f", label="Caught by internal QA")
    ax.axvline(2.5, ls="--", color="#999"); ax.text(2.55, ax.get_ylim()[1] * 0.92, "triage process starts", fontsize=8)
    ax.legend(frameon=False, fontsize=8); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(REPORTS / "defect_trend.png", dpi=150); plt.close(fig)

    md = [
        f"# Release Review — {current}",
        "",
        f"## Gate decision: **{gate.decision}**",
        "",
        gate.to_frame().to_markdown(index=False),
        "",
        "## Open risk register",
        "",
        risks_reg[risks_reg["release_id"] == current]
            .drop(columns=["release_id"]).to_markdown(index=False),
        "",
        "![Risk heat map](risk_heatmap.png)",
        "",
        "## Defect trend",
        "",
        f"User-reported defects: baseline avg {trend['baseline_avg']} → latest {trend['latest']} "
        f"({trend['change_pct']:+.1f}%).",
        "",
        "![Defect trend](defect_trend.png)",
        "",
        by_rel.to_markdown(index=False),
        "",
        "## Component hotspots (user-reported)",
        "",
        hot.to_markdown(index=False),
        "",
    ]
    (REPORTS / "release_review.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Gate for {current}: {gate.decision}. Report in {REPORTS / 'release_review.md'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["build", "report"])
    args = ap.parse_args()
    {"build": build, "report": report}[args.command]()


if __name__ == "__main__":
    main()
