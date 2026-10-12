"""Run this file to run the whole project.

It builds the database with sample data, runs the release review,
and tells you where the results are.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src"))

from release_risk import cli  # noqa: E402

print("Step 1/2: building the database")
cli.build()
print("Step 2/2: running the release review")
cli.report()
print()
print("DONE. Results:")
print(f"  Report : {ROOT / 'reports' / 'release_review.md'}")
print(f"  Charts : {ROOT / 'reports' / 'risk_heatmap.png'}")
print(f"           {ROOT / 'reports' / 'defect_trend.png'}")
