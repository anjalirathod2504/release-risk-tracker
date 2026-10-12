-- name: open_risks_by_score
-- Risk register sorted by exposure (probability x impact), open/mitigating only.
SELECT r.release_id, r.risk_id, r.title, r.category, r.owner, r.status,
       r.probability, r.impact, r.probability * r.impact AS score,
       CASE WHEN r.probability * r.impact >= 15 THEN 'High'
            WHEN r.probability * r.impact >= 8  THEN 'Medium'
            ELSE 'Low' END AS rating
FROM risks r
WHERE r.status <> 'Closed'
ORDER BY score DESC, r.raised_on;

-- name: defects_by_release
-- Defect counts per release split by source and severity; base for trend analysis.
SELECT d.release_id, rel.planned_date,
       COUNT(*)                                                     AS total_defects,
       SUM(CASE WHEN d.source = 'User Reported' THEN 1 ELSE 0 END)  AS user_reported,
       SUM(CASE WHEN d.severity IN ('S1','S2') THEN 1 ELSE 0 END)    AS high_severity,
       SUM(CASE WHEN d.closed_on IS NULL THEN 1 ELSE 0 END)         AS still_open,
       ROUND(AVG(julianday(d.closed_on) - julianday(d.opened_on)), 1) AS avg_days_to_close
FROM defects d
JOIN releases rel ON rel.release_id = d.release_id
GROUP BY d.release_id
ORDER BY rel.planned_date;

-- name: component_hotspots
-- Components generating the most user-reported defects across all releases.
SELECT component,
       COUNT(*) AS user_reported_defects,
       SUM(CASE WHEN severity IN ('S1','S2') THEN 1 ELSE 0 END) AS high_severity
FROM defects
WHERE source = 'User Reported'
GROUP BY component
ORDER BY user_reported_defects DESC
LIMIT 5;
