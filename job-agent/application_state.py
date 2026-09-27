"""Versioned local job state; migrations are explicit and transactional."""
from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
from employer_registry import load_registry, source_map

STATES = ("NEW", "SHORTLISTED", "APPLIED", "INTERVIEW", "REJECTED", "OFFER", "SKIP")
FRESH_STATES = {"NEW", "SHORTLISTED"}
DEFAULT_PATH = Path(__file__).resolve().parent / "application_state.sqlite3"
SCHEMA_VERSION = 3
# The original unversioned layout is logical v1 (user_version 0 or 1).
LEGACY_SQL = """CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL CHECK (status IN
        ('NEW', 'SHORTLISTED', 'APPLIED', 'INTERVIEW', 'REJECTED', 'OFFER', 'SKIP')),
    job_json TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    status_updated_at TEXT NOT NULL
)"""
SCHEMA = {
    "employers": """CREATE TABLE employers (
        employer_id TEXT PRIMARY KEY NOT NULL,
        display_name TEXT NOT NULL,
        pool TEXT NOT NULL CHECK (pool IN ('ACTIVE', 'BENCH', 'PAUSED')),
        registry_json TEXT NOT NULL,
        configured INTEGER NOT NULL CHECK (configured IN (0, 1))
    )""",
    "employer_sources": """CREATE TABLE employer_sources (
        board TEXT PRIMARY KEY NOT NULL COLLATE NOCASE,
        employer_id TEXT NOT NULL REFERENCES employers(employer_id),
        configured INTEGER NOT NULL CHECK (configured IN (0, 1)),
        UNIQUE (board, employer_id)
    )""",
    "jobs": """CREATE TABLE jobs (
        id TEXT PRIMARY KEY NOT NULL,
        status TEXT NOT NULL CHECK (status IN
            ('NEW', 'SHORTLISTED', 'APPLIED', 'INTERVIEW', 'REJECTED', 'OFFER', 'SKIP')),
        job_json TEXT NOT NULL,
        first_seen TEXT NOT NULL,
        last_seen TEXT NOT NULL,
        status_updated_at TEXT NOT NULL,
        employer_id TEXT NOT NULL,
        source_board TEXT NOT NULL,
        FOREIGN KEY (source_board, employer_id)
            REFERENCES employer_sources(board, employer_id)
    )""",
    "source_runs": """CREATE TABLE source_runs (
        observation_id INTEGER PRIMARY KEY,
        board TEXT NOT NULL REFERENCES employer_sources(board),
        observed_at TEXT NOT NULL,
        success INTEGER NOT NULL CHECK (success IN (0, 1)),
        fetched_count INTEGER,
        relevant_count INTEGER,
        error_kind TEXT,
        CHECK ((success = 1 AND fetched_count IS NOT NULL AND relevant_count IS NOT NULL
                AND fetched_count >= 0 AND relevant_count >= 0
                AND relevant_count <= fetched_count AND error_kind IS NULL)
            OR (success = 0 AND fetched_count IS NULL AND relevant_count IS NULL
                AND error_kind IS NOT NULL))
    )"""
}


V2_SCHEMA = dict(SCHEMA)
LIFECYCLE_SCHEMA = {
    "applications": """CREATE TABLE applications (
        application_id INTEGER PRIMARY KEY,
        employer_id TEXT NOT NULL REFERENCES employers(employer_id),
        job_id TEXT NOT NULL REFERENCES jobs(id),
        title TEXT NOT NULL,
        submitted_at TEXT,
        recorded_at TEXT NOT NULL,
        provenance TEXT NOT NULL CHECK (provenance = 'EXPLICIT_USER')
    )""",
    "application_events": """CREATE TABLE application_events (
        event_id INTEGER PRIMARY KEY,
        application_id INTEGER NOT NULL REFERENCES applications(application_id),
        event TEXT NOT NULL CHECK (event IN
            ('APPLIED', 'SCREEN', 'INTERVIEW', 'OFFER', 'REJECTED', 'WITHDRAWN', 'CLOSED')),
        engagement TEXT NOT NULL CHECK (engagement IN ('UNKNOWN', 'NO', 'YES')),
        occurred_at TEXT,
        recorded_at TEXT NOT NULL,
        reason TEXT
    )""",
    "legacy_application_facts": """CREATE TABLE legacy_application_facts (
        fact_id INTEGER PRIMARY KEY,
        job_id TEXT NOT NULL REFERENCES jobs(id),
        status TEXT NOT NULL CHECK (status IN ('APPLIED', 'INTERVIEW', 'OFFER', 'REJECTED')),
        status_updated_at TEXT NOT NULL,
        recorded_at TEXT NOT NULL
    )""",
    "employer_decisions": """CREATE TABLE employer_decisions (
        decision_id INTEGER PRIMARY KEY,
        employer_id TEXT NOT NULL REFERENCES employers(employer_id),
        job_id TEXT REFERENCES jobs(id),
        application_id INTEGER REFERENCES applications(application_id),
        action TEXT NOT NULL CHECK (action IN
            ('OVERRIDE', 'REVIEW_CLEARED', 'LEGACY_ELIGIBLE', 'LEGACY_REVIEW', 'LEGACY_LINKED')),
        context TEXT NOT NULL,
        reason TEXT NOT NULL,
        recorded_at TEXT NOT NULL
    )""",
}
SCHEMA.update(LIFECYCLE_SCHEMA)


def _capture_legacy(connection):
    # These are copies of factual labels, not inferred application events/dates.
    connection.execute("""INSERT INTO legacy_application_facts
        (job_id, status, status_updated_at, recorded_at)
        SELECT id, status, status_updated_at, ? FROM jobs
        WHERE status IN ('APPLIED', 'INTERVIEW', 'OFFER', 'REJECTED')""",
        (datetime.now(timezone.utc).isoformat(),))


def _normalized(sql):
    # Normalize formatting, never the values of CHECK constraint string literals.
    parts = re.split(r"('(?:''|[^'])*')", sql)
    return "".join(part if index % 2 else re.sub(r"\s+", "", part).lower()
                   for index, part in enumerate(parts))


def _schema(connection):
    # Reject partial layouts, triggers/views and unreviewed schema alterations.
    return {(kind, name): _normalized(sql) for kind, name, sql in connection.execute(
        "SELECT type, name, sql FROM sqlite_master WHERE name NOT GLOB 'sqlite_*'")}


def _check_schema(connection, definitions):
    expected = {("table", name): _normalized(sql) for name, sql in definitions.items()}
    if _schema(connection) != expected:
        raise ValueError("Unrecognized or partial application-state schema; no changes made")
    if connection.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
        raise ValueError("Application-state integrity check failed")
    if connection.execute("PRAGMA foreign_key_check").fetchone():
        raise ValueError("Application-state foreign key check failed")


def _sync_registry(connection, registry):
    mappings = source_map(registry)
    for board, entry in mappings.items():
        old = connection.execute(
            "SELECT employer_id FROM employer_sources WHERE board=?", (board,)).fetchone()
        if old and old[0] != entry["employer_id"]:
            raise ValueError("A persisted source cannot be reassigned to another employer")
    # Removal is configuration absence, not deletion or automatic pool movement.
    connection.execute("UPDATE employers SET configured=0")
    connection.execute("UPDATE employer_sources SET configured=0")
    for entry in registry["employers"]:
        connection.execute("""INSERT INTO employers
            (employer_id, display_name, pool, registry_json, configured) VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(employer_id) DO UPDATE SET display_name=excluded.display_name,
                pool=excluded.pool, registry_json=excluded.registry_json, configured=1""",
            (entry["employer_id"], entry["display_name"], entry["pool"],
             json.dumps(entry, ensure_ascii=False)))
        for board in entry["greenhouse_boards"]:
            connection.execute("""INSERT INTO employer_sources (board, employer_id, configured)
                VALUES (?, ?, 1) ON CONFLICT(board) DO UPDATE SET configured=1""",
                (board, entry["employer_id"]))


def _identity(job_id, mappings):
    if not isinstance(job_id, str) or ":" not in job_id:
        raise ValueError("Job requires an explicit source-prefixed ID")
    board, suffix = job_id.split(":", 1)
    if not suffix or board not in mappings:
        raise ValueError("Job source has no explicit registry mapping; resolve before proceeding")
    return mappings[board]["employer_id"], board


def _migrate(connection, registry):
    mappings = source_map(registry)
    # DDL and copied rows share the same explicit transaction; no executescript.
    connection.execute("ALTER TABLE jobs RENAME TO legacy_jobs")
    for sql in SCHEMA.values():
        connection.execute(sql)
    _sync_registry(connection, registry)
    for row in connection.execute("SELECT * FROM legacy_jobs").fetchall():
        job_id, status, snapshot, first, last, updated = row
        employer_id, board = _identity(job_id, mappings)
        try:
            job = json.loads(snapshot)
        except (ValueError, TypeError):
            raise ValueError("Invalid legacy snapshot; migration stopped") from None
        if (not isinstance(job, dict) or job.get("id") != job_id or status not in STATES
                or any(not isinstance(v, str) or not v for v in (first, last, updated))):
            raise ValueError("Invalid legacy record; migration stopped")
        connection.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (*row, employer_id, board))
    connection.execute("DROP TABLE legacy_jobs")


def connect(path, *, migration_registry=None):
    # Normal runs never implicitly migrate a user's legacy database.
    connection = sqlite3.connect(path)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("BEGIN IMMEDIATE")
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        objects = _schema(connection)
        if version == 0 and not objects:
            for sql in SCHEMA.values():
                connection.execute(sql)
            connection.execute("PRAGMA user_version=3")
        elif version in (0, 1):
            _check_schema(connection, {"jobs": LEGACY_SQL})
            if migration_registry is None:
                raise ValueError("Legacy v1 database requires explicit migration after approved backup/restoration planning")
            _migrate(connection, migration_registry)
            _capture_legacy(connection)
            connection.execute("PRAGMA user_version=3")
        elif version == 2:
            _check_schema(connection, V2_SCHEMA)
            if migration_registry is None:
                raise ValueError("Legacy v2 database requires explicit migration after approved backup/restoration planning")
            for sql in LIFECYCLE_SCHEMA.values():
                connection.execute(sql)
            _capture_legacy(connection)
            connection.execute("PRAGMA user_version=3")
        elif version != SCHEMA_VERSION:
            raise ValueError("Unsupported application-state schema version")
        _check_schema(connection, SCHEMA)
        connection.commit()
    except Exception:
        connection.rollback()
        connection.close()
        raise
    return connection


def migrate_database(path, registry):
    """Explicit opt-in only; caller must arrange approved backup and restoration."""
    source_map(registry)  # Validate before opening even a synthetic database.
    if not Path(path).is_file():
        raise ValueError("Migration requires an existing database")
    with closing(connect(path, migration_registry=registry)):
        pass


def record_jobs(path, jobs, registry=None, observations=()):
    """Atomically save configuration, listing refreshes and observed source facts."""
    registry = load_registry() if registry is None else registry
    mappings = source_map(registry)
    now = datetime.now(timezone.utc).isoformat()
    with closing(connect(path)) as connection, connection:
        _sync_registry(connection, registry)
        for job in jobs:
            employer_id, board = _identity(job["id"], mappings)
            if job.get("employer_id", employer_id) != employer_id:
                raise ValueError("Job employer identity conflicts with explicit mapping")
            connection.execute("""INSERT INTO jobs
                (id, status, job_json, first_seen, last_seen, status_updated_at, employer_id, source_board)
                VALUES (?, 'NEW', ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    job_json=excluded.job_json, last_seen=excluded.last_seen""",
                (job["id"], json.dumps(job, ensure_ascii=False), now, now, now, employer_id, board))
        for observation in observations:
            board = observation["board"]
            if board not in mappings:
                raise ValueError("Observation source has no explicit mapping")
            connection.execute("""INSERT INTO source_runs
                (board, observed_at, success, fetched_count, relevant_count, error_kind)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (board, observation["observed_at"], observation["success"],
                 observation["fetched_count"], observation["relevant_count"],
                 observation["error_kind"]))
        return dict(connection.execute("SELECT id, status FROM jobs"))


def mark_job(path, job_id, status):
    if status not in STATES:
        raise ValueError(f"Status must be one of: {', '.join(STATES)}")
    with closing(connect(path)) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        if connection.execute("SELECT 1 FROM applications WHERE job_id=?", (job_id,)).fetchone():
            raise ValueError("Job has explicit application history; use application lifecycle commands instead of --mark")
        now = datetime.now(timezone.utc).isoformat()
        cursor = connection.execute(
            "UPDATE jobs SET status=?, status_updated_at=? WHERE id=?",
            (status, now, job_id))
        if cursor.rowcount != 1:
            raise ValueError("Unknown job ID; run Scout and use an ID from its report or --history")
        if status in {"APPLIED", "INTERVIEW", "OFFER", "REJECTED"}:
            connection.execute("""INSERT INTO legacy_application_facts
                (job_id, status, status_updated_at, recorded_at) VALUES (?, ?, ?, ?)""",
                (job_id, status, now, now))


def read_history(path):
    with closing(connect(path)) as connection:
        return [{"id": job_id, "status": status, "job": json.loads(snapshot),
                 "first_seen": first, "last_seen": last, "status_updated_at": updated,
                 "employer_id": employer_id}
                for job_id, status, snapshot, first, last, updated, employer_id in connection.execute(
                    "SELECT id, status, job_json, first_seen, last_seen, status_updated_at, employer_id "
                    "FROM jobs ORDER BY first_seen, id")]
