"""SQLite helpers: create the schema, load sample data, run named queries."""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = ROOT / "sql"


def connect(path: str | Path = ":memory:") -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_schema(con: sqlite3.Connection) -> None:
    con.executescript((SQL_DIR / "schema.sql").read_text())


def load_frames(con: sqlite3.Connection, releases: pd.DataFrame, risks: pd.DataFrame,
                defects: pd.DataFrame) -> None:
    for name, df in (("releases", releases), ("risks", risks), ("defects", defects)):
        df.to_sql(name, con, if_exists="append", index=False)
    con.commit()


def named_queries() -> dict[str, str]:
    """Parse `-- name: xyz` blocks from sql/queries.sql."""
    text = (SQL_DIR / "queries.sql").read_text()
    parts = re.split(r"^-- name:\s*(\w+)\s*$", text, flags=re.M)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}


def query(con: sqlite3.Connection, name: str) -> pd.DataFrame:
    return pd.read_sql_query(named_queries()[name], con)
