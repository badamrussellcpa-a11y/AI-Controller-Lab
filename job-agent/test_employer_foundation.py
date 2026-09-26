"""Synthetic-only registry, migration and source-observation acceptance."""
from contextlib import closing, redirect_stdout, redirect_stderr
from copy import deepcopy
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import application_state as state
from employer_registry import load_registry, validate_registry, select_sources
from job_scout import main
from test_job_scout import fixture, TEST_REGISTRY

# Independent fixture copied from the pre-versioning schema, not new migration DDL.
OLD_SCHEMA = """CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL CHECK (status IN
        ('NEW', 'SHORTLISTED', 'APPLIED', 'INTERVIEW', 'REJECTED', 'OFFER', 'SKIP')),
    job_json TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    status_updated_at TEXT NOT NULL
)"""


class FoundationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.db = self.folder / "synthetic.sqlite3"
        self.registry = deepcopy(TEST_REGISTRY)
        self.config = self.folder / "employers.json"

    def save_config(self):
        self.config.write_text(json.dumps(self.registry), encoding="utf-8")
        return self.config

    def query(self, sql, params=()):
        with closing(sqlite3.connect(self.db)) as connection:
            return connection.execute(sql, params).fetchall()

    def legacy(self, ids=None, version=0):
        ids = ids or [f"test:{n}" for n in range(len(state.STATES))]
        rows = [(job_id, state.STATES[n % len(state.STATES)],
                 json.dumps(fixture(id=job_id), indent=2) + "  ",
                 "2026-01-01T00:00:00Z", "2026-02-02T00:00:00Z", "2026-03-03T00:00:00Z")
                for n, job_id in enumerate(ids)]
        with closing(sqlite3.connect(self.db)) as connection, connection:
            connection.execute(OLD_SCHEMA)
            connection.executemany("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?)", rows)
            connection.execute(f"PRAGMA user_version={version}")
        return rows

    def run_scout(self, jobs=None, extra=()):
        self.save_config()
        with patch("job_scout.fetch_jobs", return_value=jobs or []), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return main(["--state-file", str(self.db), "--registry", str(self.config),
                         "--output", str(self.folder / "reports"), *extra])

    def test_pilot_registry_preserves_four_sources_and_unknowns(self):
        registry = load_registry()
        sources = select_sources(registry)
        self.assertEqual(list(sources), ["rocketlab", "spacex", "figma", "reddit"])
        self.assertTrue(all(e["approval_status"] == "PILOT" for e in sources.values()))
        self.assertTrue(all(e["approval_date"] is None and e["industry"] is None
                            for e in sources.values()))
        self.assertEqual(len(sources), 4)  # Not a required ten or approved final pool.

    def test_invalid_canonical_ids_and_duplicates(self):
        for value in ("", "../x", "Bad ID", "name\ncommand", "a" * 65, None, True):
            registry = deepcopy(self.registry)
            registry["employers"][0]["employer_id"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_registry(registry)
        self.registry["employers"].append(deepcopy(self.registry["employers"][0]))
        with self.assertRaises(ValueError):
            validate_registry(self.registry)

    def test_invalid_source_and_ambiguous_mappings(self):
        for value in ("../test", "https://host", "test\n", "", None, "GOOD"):
            registry = deepcopy(self.registry)
            registry["employers"][0]["greenhouse_boards"] = [value]
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_registry(registry)
        self.registry["employers"][0]["greenhouse_boards"] = ["test", "test"]
        with self.assertRaises(ValueError):
            validate_registry(self.registry)

    def test_invalid_structure_dates_and_duplicate_json_keys(self):
        cases = [{}, {"version": True, "employers": []}, {"version": 2, "employers": []}]
        for changes in ({"pool": []}, {"approval_status": "UNKNOWN"}, {"approval_date": "yesterday"},
                        {"industry": 123}, {"display_name": "x\n#payload"}, {"unrecognized": "typo"},
                        {"approval_status": "PENDING", "pool": "ACTIVE"}):
            registry = deepcopy(self.registry)
            registry["employers"][0].update(changes)
            cases.append(registry)
        for registry in cases:
            with self.subTest(registry=registry), self.assertRaises(ValueError):
                validate_registry(registry)
        self.config.write_text('{"version":1,"version":1,"employers":[]}', encoding="utf-8")
        with self.assertRaises(ValueError):
            load_registry(self.config)

    def test_multiple_explicit_boards_share_employer_and_nulls_stay_unknown(self):
        entry = self.registry["employers"][0]
        entry.update(approval_status="APPROVED", approval_date=None, industry=None)
        entry["greenhouse_boards"].append("second")
        state.record_jobs(self.db, [fixture(), fixture(id="second:2")], self.registry)
        self.assertEqual({r["employer_id"] for r in state.read_history(self.db)}, {"fixture-test"})
        saved = json.loads(self.query("SELECT registry_json FROM employers WHERE employer_id='fixture-test'")[0][0])
        self.assertIsNone(saved["industry"])
        self.assertIsNone(saved["approval_date"])
        self.assertNotIn("size_band", saved)

    def test_pool_validation_selection_and_no_auto_movement(self):
        for entry, pool in zip(self.registry["employers"], ("ACTIVE", "BENCH", "PAUSED")):
            entry["pool"] = pool
        self.assertEqual(list(select_sources(self.registry)), ["test"])
        with self.assertRaises(ValueError):
            select_sources(self.registry, ["good"])
        state.record_jobs(self.db, [], self.registry)
        before = self.query("SELECT employer_id, pool FROM employers ORDER BY employer_id")
        state.record_jobs(self.db, [], self.registry, [{
            "board": "test", "observed_at": "2026-09-26T00:00:00Z", "success": True,
            "fetched_count": 0, "relevant_count": 0, "error_kind": None}])
        self.assertEqual(self.query("SELECT employer_id, pool FROM employers ORDER BY employer_id"), before)
        self.registry["employers"][0]["pool"] = "AUTO"
        with self.assertRaises(ValueError):
            validate_registry(self.registry)

    def test_display_rename_keeps_identity_and_source_reassignment_fails(self):
        state.record_jobs(self.db, [fixture()], self.registry)
        self.registry["employers"][0]["display_name"] = "Renamed Employer"
        state.record_jobs(self.db, [], self.registry)
        self.assertEqual(state.read_history(self.db)[0]["employer_id"], "fixture-test")
        self.assertEqual(self.query("SELECT display_name FROM employers WHERE employer_id='fixture-test'"),
                         [("Renamed Employer",)])
        self.registry["employers"][0]["employer_id"] = "different-company"
        with self.assertRaises(ValueError):
            state.record_jobs(self.db, [], self.registry)
        self.assertEqual(self.query("SELECT employer_id FROM employer_sources WHERE board='test'"),
                         [("fixture-test",)])

    def test_removing_configuration_retains_jobs_and_mark_history(self):
        state.record_jobs(self.db, [fixture()], self.registry)
        state.mark_job(self.db, "test:1", "APPLIED")
        before = state.read_history(self.db)
        self.registry["employers"] = []
        state.record_jobs(self.db, [], self.registry)
        self.assertEqual(state.read_history(self.db), before)
        self.assertEqual(self.query("SELECT configured, pool FROM employers WHERE employer_id='fixture-test'"),
                         [(0, "ACTIVE")])
        state.mark_job(self.db, "test:1", "NEW")
        self.assertEqual(state.read_history(self.db)[0]["status"], "NEW")

    def test_fresh_schema_and_foreign_keys(self):
        state.record_jobs(self.db, [fixture()], self.registry)
        self.assertEqual(self.query("PRAGMA user_version"), [(2,)])
        self.assertEqual(self.query("PRAGMA foreign_key_check"), [])
        with closing(state.connect(self.db)) as connection:
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone(), (1,))
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("UPDATE jobs SET employer_id='unknown'")

    def test_unversioned_legacy_migration_preserves_every_existing_value(self):
        before = self.legacy()
        state.migrate_database(self.db, self.registry)
        after = self.query("SELECT id, status, job_json, first_seen, last_seen, status_updated_at FROM jobs")
        self.assertEqual(after, before)
        self.assertEqual(self.query("PRAGMA user_version"), [(2,)])
        self.assertEqual({r["employer_id"] for r in state.read_history(self.db)}, {"fixture-test"})
        self.assertEqual(self.query("SELECT * FROM source_runs"), [])  # No invented observations.
        self.assertEqual({row[0] for row in self.query("SELECT name FROM sqlite_master WHERE type='table'")},
                         {"jobs", "employers", "employer_sources", "source_runs"})

    def test_explicit_version_one_supported_and_migration_is_idempotent(self):
        self.legacy(version=1)
        state.migrate_database(self.db, self.registry)
        before = state.read_history(self.db)
        state.migrate_database(self.db, self.registry)
        self.assertEqual(state.read_history(self.db), before)

    def test_legacy_normal_commands_refuse_without_modifying_file_or_fetching(self):
        self.legacy()
        before = self.db.read_bytes()
        for extra in ((), ("--history",), ("--mark", "test:0", "APPLIED")):
            with self.subTest(extra=extra):
                self.save_config()
                with patch("job_scout.fetch_jobs") as fetch, redirect_stderr(io.StringIO()):
                    self.assertEqual(main(["--state-file", str(self.db), "--registry", str(self.config), *extra]), 3)
                    fetch.assert_not_called()
                self.assertEqual(self.db.read_bytes(), before)

    def test_future_schema_fails_closed(self):
        state.record_jobs(self.db, [fixture()], self.registry)
        with closing(sqlite3.connect(self.db)) as connection:
            connection.execute("PRAGMA user_version=999")
        before = self.db.read_bytes()
        with self.assertRaises(ValueError):
            state.read_history(self.db)
        self.assertEqual(self.db.read_bytes(), before)

    def test_partial_or_altered_schema_fails_closed(self):
        self.legacy()
        with closing(sqlite3.connect(self.db)) as connection:
            connection.execute("CREATE TABLE employers (id TEXT)")
        before = self.db.read_bytes()
        with self.assertRaises(ValueError):
            state.migrate_database(self.db, self.registry)
        self.assertEqual(self.db.read_bytes(), before)

    def test_version_two_marker_cannot_hide_missing_tables(self):
        self.legacy(version=2)
        before = self.db.read_bytes()
        with self.assertRaises(ValueError):
            state.read_history(self.db)
        self.assertEqual(self.db.read_bytes(), before)

    def test_changed_legacy_constraints_are_not_treated_as_formatting(self):
        with closing(sqlite3.connect(self.db)) as connection:
            connection.execute(OLD_SCHEMA.replace("'NEW'", "'N E W'"))
        before = self.db.read_bytes()
        with self.assertRaises(ValueError):
            state.migrate_database(self.db, self.registry)
        self.assertEqual(self.db.read_bytes(), before)

    def test_same_names_do_not_merge_and_sql_text_is_only_data(self):
        name = "Example'); DROP TABLE jobs; --"
        self.registry["employers"][0]["display_name"] = name
        self.registry["employers"][1]["display_name"] = name
        state.record_jobs(self.db, [fixture(), fixture(id="good:2")], self.registry)
        self.assertEqual({r["employer_id"] for r in state.read_history(self.db)},
                         {"fixture-test", "fixture-good"})
        self.assertEqual(self.query("SELECT COUNT(*) FROM employers WHERE display_name=?", (name,)), [(2,)])

    def test_unmapped_legacy_job_rolls_back_ddl_and_rows(self):
        rows = self.legacy(["test:1", "unmapped:2"])
        before = self.db.read_bytes()
        with self.assertRaises(ValueError):
            state.migrate_database(self.db, self.registry)
        self.assertEqual(self.db.read_bytes(), before)
        self.assertEqual(self.query("SELECT * FROM jobs"), rows)
        self.assertEqual(self.query("PRAGMA user_version"), [(0,)])
        self.assertEqual(self.query("SELECT name FROM sqlite_master WHERE type='table'"), [("jobs",)])

    def test_ambiguous_mapping_stops_before_migration(self):
        self.legacy()
        before = self.db.read_bytes()
        self.registry["employers"][1]["greenhouse_boards"] = ["test"]
        with self.assertRaises(ValueError):
            state.migrate_database(self.db, self.registry)
        self.assertEqual(self.db.read_bytes(), before)

    def test_failure_after_migration_work_rolls_back_version_and_schema(self):
        self.legacy()
        before = self.db.read_bytes()
        real_check = state._check_schema
        def fail_final(connection, definitions):
            real_check(connection, definitions)
            if "employers" in definitions:
                raise sqlite3.OperationalError("synthetic failure before commit")
        with patch("application_state._check_schema", side_effect=fail_final):
            with self.assertRaises(sqlite3.OperationalError):
                state.migrate_database(self.db, self.registry)
        self.assertEqual(self.db.read_bytes(), before)
        self.assertEqual(self.query("PRAGMA user_version"), [(0,)])

    def test_malformed_legacy_snapshot_rolls_back(self):
        self.legacy()
        with closing(sqlite3.connect(self.db)) as connection, connection:
            connection.execute("UPDATE jobs SET job_json='{}' WHERE id='test:0'")
        before = self.db.read_bytes()
        with self.assertRaises(ValueError):
            state.migrate_database(self.db, self.registry)
        self.assertEqual(self.db.read_bytes(), before)

    def test_migrated_state_exclusions_mark_and_history_across_processes(self):
        self.legacy()
        self.save_config()
        result = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("job_scout.py")),
                                 "--registry", str(self.config), "--state-file", str(self.db),
                                 "--migrate-state"], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.run_scout([fixture(id=f"test:{n}") for n in range(7)],
                                       ("--boards", "test")), 0)
        run = json.loads(next((self.folder / "reports").glob("*.json")).read_text(encoding="utf-8"))
        self.assertEqual([j["id"] for j in run["jobs"]], ["test:0", "test:1"])
        state.mark_job(self.db, "test:0", "APPLIED")
        self.assertEqual(len(state.read_history(self.db)), 7)
        self.assertEqual(state.read_history(self.db)[0]["status"], "APPLIED")

    def test_source_counts_are_observed_not_researched_and_failures_are_null(self):
        self.save_config()
        jobs = [fixture(), fixture(), fixture(id="test:2", title="Software Engineer"),
                fixture(id="test:3", location="Austin, TX")]
        with patch("job_scout.fetch_jobs", side_effect=[jobs, [], OSError("private-error-payload")]), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--registry", str(self.config), "--state-file", str(self.db),
                                   "--output", str(self.folder / "reports")]), 2)
        self.assertEqual(self.query("SELECT board, success, fetched_count, relevant_count, error_kind FROM source_runs"),
                         [("test", 1, 4, 2, None), ("good", 1, 0, 0, None), ("bad", 0, None, None, "OSError")])
        # Reopen through another process; failures cannot be averaged in as zero yield.
        script = "import sqlite3,sys,json; c=sqlite3.connect(sys.argv[1]); print(json.dumps(c.execute('SELECT COUNT(*) FROM source_runs').fetchone()))"
        result = subprocess.run([sys.executable, "-B", "-c", script, str(self.db)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [3])
        self.assertTrue(all(row[0] for row in self.query("SELECT observed_at FROM source_runs")))
        self.assertNotIn("private-error-payload", str(self.query("SELECT * FROM source_runs")))

    def test_bad_observation_rolls_back_entire_batch(self):
        state.record_jobs(self.db, [fixture()], self.registry)
        before = state.read_history(self.db)
        with self.assertRaises(sqlite3.IntegrityError):
            state.record_jobs(self.db, [fixture(id="test:2")], self.registry, [{
                "board": "test", "observed_at": "2026-09-26T00:00:00Z", "success": False,
                "fetched_count": 0, "relevant_count": 0, "error_kind": "OSError"}])
        self.assertEqual(state.read_history(self.db), before)
        self.assertEqual(self.query("SELECT * FROM source_runs"), [])

    def test_unknown_or_inactive_requested_source_stops_before_fetch(self):
        self.registry["employers"][0]["pool"] = "BENCH"
        self.save_config()
        for board in ("test", "unmapped"):
            with patch("job_scout.fetch_jobs") as fetch, redirect_stderr(io.StringIO()):
                self.assertEqual(main(["--registry", str(self.config), "--state-file", str(self.db),
                                       "--boards", board]), 3)
                fetch.assert_not_called()
            self.assertFalse(self.db.exists())

    def test_pilot_default_run_preserves_all_four_feeds_and_top_five(self):
        calls = []
        def fetch(board, company):
            calls.append((board, company))
            return [fixture(id=f"{board}:{n}", company=company) for n in range(2)]
        with patch("job_scout.fetch_jobs", side_effect=fetch), redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--state-file", str(self.db), "--output",
                                   str(self.folder / "reports")]), 0)
        self.assertEqual(calls, [("rocketlab", "Rocket Lab"), ("spacex", "SpaceX"),
                                 ("figma", "Figma"), ("reddit", "Reddit")])
        run = json.loads(next((self.folder / "reports").glob("*.json")).read_text(encoding="utf-8"))
        self.assertEqual(len(run["jobs"]), 5)
        self.assertEqual(run["active_employer_count"], 4)
        self.assertEqual(len(state.read_history(self.db)), 8)

    def test_inconsistent_source_job_identity_is_failed_not_guessed(self):
        self.assertEqual(self.run_scout([fixture(id="other:1")], ("--boards", "test")), 1)
        self.assertEqual(state.read_history(self.db), [])
        self.assertEqual(self.query("SELECT success, fetched_count FROM source_runs"), [(0, None)])


if __name__ == "__main__":
    unittest.main()
