BEGIN;

INSERT OR IGNORE INTO TimeClockArchive (job_id, start, end, version)
SELECT job_id, start, end, version
FROM TimeClock
WHERE end IS NOT NULL
  AND start < DATE('now', 'localtime');

DELETE FROM TimeClock
WHERE end IS NOT NULL
  AND start < DATE('now', 'localtime');

COMMIT;
