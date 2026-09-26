"""Local application records, keyed by the feed's stable board:job ID."""
from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3

STATES = ("NEW", "SHORTLISTED", "APPLIED", "INTERVIEW", "REJECTED", "OFFER", "SKIP")
FRESH_STATES = {"NEW", "SHORTLISTED"}
DEFAULT_PATH = Path(__file__).resolve().parent / "application_state.sqlite3"


def connect(path):
    # Do not silently replace unreadable/corrupt state: losing exclusions is unsafe.
    connection = sqlite3.connect(path)
    try:
        connection.execute("""CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL CHECK (status IN
                ('NEW', 'SHORTLISTED', 'APPLIED', 'INTERVIEW', 'REJECTED', 'OFFER', 'SKIP')),
            job_json TEXT NOT NULL,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            status_updated_at TEXT NOT NULL
        )""")
        connection.commit()
    except Exception:
        connection.close()
        raise
    return connection


def record_jobs(path, jobs):
    """Refresh listing details without resetting status or deleting absent jobs."""
    now = datetime.now(timezone.utc).isoformat()
    with closing(connect(path)) as connection, connection:
        for job in jobs:
            connection.execute("""INSERT INTO jobs
                (id, status, job_json, first_seen, last_seen, status_updated_at)
                VALUES (?, 'NEW', ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    job_json=excluded.job_json, last_seen=excluded.last_seen""",
                (job["id"], json.dumps(job, ensure_ascii=False), now, now, now))
        return dict(connection.execute("SELECT id, status FROM jobs"))


def mark_job(path, job_id, status):
    if status not in STATES:
        raise ValueError(f"Status must be one of: {', '.join(STATES)}")
    with closing(connect(path)) as connection, connection:
        cursor = connection.execute(
            "UPDATE jobs SET status=?, status_updated_at=? WHERE id=?",
            (status, datetime.now(timezone.utc).isoformat(), job_id))
        if cursor.rowcount != 1:
            raise ValueError("Unknown job ID; run Scout and use an ID from its report or --history")


def read_history(path):
    with closing(connect(path)) as connection:
        return [{"id": job_id, "status": status, "job": json.loads(snapshot),
                 "first_seen": first, "last_seen": last, "status_updated_at": updated}
                for job_id, status, snapshot, first, last, updated in connection.execute(
                    "SELECT id, status, job_json, first_seen, last_seen, status_updated_at "
                    "FROM jobs ORDER BY first_seen, id")]
