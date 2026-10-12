-- Release governance database (SQLite).
-- One release has many risks and many defects; milestones track the gate reviews.

CREATE TABLE IF NOT EXISTS releases (
    release_id    TEXT PRIMARY KEY,          -- e.g. 'R2026.3'
    name          TEXT NOT NULL,
    planned_date  DATE NOT NULL,
    status        TEXT NOT NULL CHECK (status IN ('Planned', 'In Progress', 'Released'))
);

CREATE TABLE IF NOT EXISTS risks (
    risk_id       TEXT PRIMARY KEY,
    release_id    TEXT NOT NULL REFERENCES releases(release_id),
    title         TEXT NOT NULL,
    category      TEXT NOT NULL,             -- Schedule, Technical, Resource, Dependency, Quality
    probability   INTEGER NOT NULL CHECK (probability BETWEEN 1 AND 5),
    impact        INTEGER NOT NULL CHECK (impact BETWEEN 1 AND 5),
    owner         TEXT NOT NULL,
    status        TEXT NOT NULL CHECK (status IN ('Open', 'Mitigating', 'Closed')),
    raised_on     DATE NOT NULL,
    mitigation    TEXT
);

CREATE TABLE IF NOT EXISTS defects (
    defect_id     TEXT PRIMARY KEY,
    release_id    TEXT NOT NULL REFERENCES releases(release_id),
    component     TEXT NOT NULL,
    severity      TEXT NOT NULL CHECK (severity IN ('S1', 'S2', 'S3', 'S4')),
    source        TEXT NOT NULL CHECK (source IN ('Internal QA', 'User Reported')),
    opened_on     DATE NOT NULL,
    closed_on     DATE
);

CREATE INDEX IF NOT EXISTS idx_defects_release ON defects(release_id);
CREATE INDEX IF NOT EXISTS idx_risks_release   ON risks(release_id);
