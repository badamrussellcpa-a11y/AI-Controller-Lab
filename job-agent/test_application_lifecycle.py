"""Task 4 acceptance: invented employers/jobs and isolated temporary state only."""
from contextlib import closing, redirect_stdout, redirect_stderr
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
import application_lifecycle as lifecycle
from job_scout import main
from test_job_scout import fixture, TEST_REGISTRY


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.db = self.folder / "synthetic.sqlite3"
        self.config = self.folder / "employers.json"
        self.config.write_text(json.dumps(TEST_REGISTRY), encoding="utf-8")
        self.jobs = [fixture(id=f"test:{n}", title="Controller" if n == 2 else "Senior Accountant")
                     for n in range(1, 8)]
        state.record_jobs(self.db, self.jobs, TEST_REGISTRY)

    def relation(self):
        return lifecycle.employer_relationships(self.db)["fixture-test"]

    def audit(self):
        return lifecycle.read_applications(self.db)

    def apply(self, job="test:1"):
        return lifecycle.record_application(self.db, job)

    def event(self, app, event, **kwargs):
        return lifecycle.record_event(self.db, app, event, **kwargs)

    def decide(self, action, reason="Synthetic reviewed decision", job_id=None, application_id=None):
        return lifecycle.decide(self.db, "fixture-test", action, reason, job_id, application_id)

    def command(self, *args):
        output, errors = io.StringIO(), io.StringIO()
        with patch("job_scout.fetch_jobs") as fetch, redirect_stdout(output), redirect_stderr(errors):
            code = main(["--state-file", str(self.db), *args])
        fetch.assert_not_called()
        return code, output.getvalue(), errors.getvalue()

    def scout(self):
        with patch("job_scout.fetch_jobs", return_value=self.jobs), redirect_stdout(io.StringIO()):
            code = main(["--state-file", str(self.db), "--registry", str(self.config),
                         "--boards", "test", "--output", str(self.folder / "reports")])
        self.assertEqual(code, 0)
        report = sorted((self.folder / "reports").glob("*.json"))[-1]
        return json.loads(report.read_text()), report.with_suffix(".md").read_text(encoding="utf-8")

    def test_application_is_explicit_and_unknowns_remain_unknown(self):
        state.mark_job(self.db, "test:1", "SHORTLISTED")
        self.assertEqual(self.audit()["applications"], [])
        app_id = self.apply()
        app = self.audit()["applications"][0]
        self.assertEqual((app["application_id"], app["employer_id"], app["job_id"]), (app_id, "fixture-test", "test:1"))
        self.assertEqual(app["title"], "Senior Accountant")
        self.assertIsNone(app["submitted_at"])
        self.assertIsNone(app["events"][0]["occurred_at"])
        self.assertEqual(app["engagement"], "UNKNOWN")
        self.assertEqual(app["provenance"], "EXPLICIT_USER")
        self.assertTrue(app["recorded_at"])

    def test_active_stages_suppress_but_all_seven_jobs_remain_visible(self):
        app = self.apply()
        for event in (None, "SCREEN", "INTERVIEW", "OFFER"):
            with self.subTest(event=event):
                if event:
                    self.event(app, event)
                run, markdown = self.scout()
                self.assertEqual(len(run["jobs"]), 7)
                self.assertEqual(run["selection_job_ids"], [])
                self.assertEqual(len(run["fresh_job_ids"]), 6)  # Job state only, not the selection queue.
                self.assertEqual(self.relation()["status"], "ACTIVE APPLICATION")
                self.assertIn("ACTIVE APPLICATION AT THIS EMPLOYER", markdown)
                self.assertIn("REVIEW BEFORE SECOND APPLICATION", markdown)
                self.assertIn("### Controller", markdown)
                self.assertEqual(next(j for j in run["jobs"] if j["id"] == "test:2")["application_status"], "NEW")

    def test_pre_engagement_rejection_releases_employer_and_retains_events(self):
        app = self.apply()
        self.event(app, "REJECTED", engagement="NO", reason="Synthetic automated rejection before any interaction")
        self.assertEqual(self.relation()["status"], "ELIGIBLE")
        run, _ = self.scout()
        self.assertEqual(len(run["selection_job_ids"]), 6)
        self.assertNotIn("test:1", run["selection_job_ids"])
        self.assertEqual([e["event"] for e in self.audit()["applications"][0]["events"]], ["APPLIED", "REJECTED"])

    def test_new_controller_arriving_during_application_is_visible_with_warning(self):
        self.jobs = [job for job in self.jobs if job["id"] != "test:2"]
        self.scout()
        self.apply()
        self.jobs.append(fixture(id="test:99", title="Controller", description=""))
        run, markdown = self.scout()
        controller = next(j for j in run["jobs"] if j["id"] == "test:99")
        self.assertEqual(controller["application_status"], "NEW")
        self.assertEqual(controller["accounting_signal_coverage"], 0)
        self.assertFalse(controller["selection_eligible"])
        self.assertIn("REVIEW BEFORE SECOND APPLICATION", controller["selection_reason"])
        self.assertIn("### Controller", markdown)

    def test_suppression_uses_canonical_identity_across_boards_not_display_names(self):
        registry = json.loads(json.dumps(TEST_REGISTRY))
        registry["employers"][0]["greenhouse_boards"].append("secondboard")
        registry["employers"][1]["display_name"] = registry["employers"][0]["display_name"]
        state.record_jobs(self.db, [fixture(id="secondboard:8"), fixture(id="good:9")], registry)
        self.apply()
        relations = lifecycle.employer_relationships(self.db)
        self.assertFalse(lifecycle.consideration(relations["fixture-test"], "secondboard:8")[0])
        self.assertTrue(lifecycle.consideration(relations["fixture-good"], "good:9")[0])
        self.decide("OVERRIDE", job_id="secondboard:8")
        self.assertTrue(lifecycle.consideration(self.relation(), "secondboard:8")[0])

    def test_screen_rejection_requires_review_and_explicit_resolution(self):
        app = self.apply()
        self.event(app, "SCREEN", occurred_at="2026-09-20")
        self.event(app, "REJECTED", reason="Synthetic process ended")
        self.assertEqual(self.relation()["status"], "REVIEW BEFORE REAPPLYING")
        before = self.audit()["applications"]
        run, markdown = self.scout()
        self.assertEqual(run["selection_job_ids"], [])
        self.assertIn("REVIEW BEFORE REAPPLYING", markdown)
        self.assertIn("### Controller", markdown)
        self.decide("REVIEW_CLEARED")
        self.assertEqual(self.relation()["status"], "ELIGIBLE")
        self.assertEqual(self.audit()["applications"], before)
        self.assertEqual(len(self.scout()[0]["selection_job_ids"]), 6)

    def test_withdrawal_after_interview_requires_review(self):
        app = self.apply()
        self.event(app, "INTERVIEW")
        self.event(app, "WITHDRAWN", reason="Synthetic withdrawal")
        self.assertEqual(self.relation()["status"], "REVIEW BEFORE REAPPLYING")
        self.assertEqual(self.audit()["applications"][0]["engagement"], "YES")
        self.assertEqual(state.read_history(self.db)[0]["status"], "SKIP")

    def test_unknown_engagement_is_not_silently_no(self):
        app = self.apply()
        self.event(app, "REJECTED", reason="Timing of past engagement unknown")
        self.assertEqual(self.audit()["applications"][0]["engagement"], "UNKNOWN")
        self.assertEqual(self.relation()["status"], "REVIEW BEFORE REAPPLYING")

    def test_earlier_no_engagement_does_not_prove_no_interaction_before_closure(self):
        app = self.apply()
        self.event(app, "OFFER", engagement="NO")
        self.event(app, "CLOSED", reason="Later interaction unknown")
        self.assertEqual(self.audit()["applications"][0]["engagement"], "UNKNOWN")
        self.assertEqual(self.relation()["status"], "REVIEW BEFORE REAPPLYING")

    def test_offer_stays_active_until_explicit_narrow_closure(self):
        app = self.apply()
        self.event(app, "OFFER")
        self.assertEqual(self.relation()["status"], "ACTIVE APPLICATION")
        self.assertEqual(self.audit()["applications"][0]["engagement"], "UNKNOWN")
        with self.assertRaises(ValueError):
            self.event(app, "SCREEN")
        self.event(app, "CLOSED", reason="Synthetic offer relationship explicitly ended")
        self.assertEqual(self.relation()["status"], "REVIEW BEFORE REAPPLYING")

    def test_override_is_specific_persistent_and_does_not_apply(self):
        self.apply()
        before = self.audit()["applications"]
        self.decide("OVERRIDE", job_id="test:2")
        relation = self.relation()
        self.assertTrue(lifecycle.consideration(relation, "test:2")[0])
        self.assertFalse(lifecycle.consideration(relation, "test:3")[0])
        run, markdown = self.scout()
        self.assertEqual(run["selection_job_ids"], ["test:2"])
        self.assertIn("OVERRIDE ACTIVE", markdown)
        self.assertEqual(self.audit()["applications"], before)
        decision = self.audit()["decisions"][0]
        self.assertTrue(decision["recorded_at"])
        self.assertEqual(decision["job_id"], "test:2")
        self.assertIn("active:1", decision["context_evidence"]["restriction_facts"])
        self.assertEqual(decision["context_evidence"]["opportunity"]["title"], "Controller")
        self.assertEqual(next(j for j in state.read_history(self.db) if j["id"] == "test:2")["status"], "NEW")
        result = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("job_scout.py")),
                                 "--state-file", str(self.db), "--employer-status", "fixture-test"],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["overrides"][0]["decision_id"], decision["decision_id"])

    def test_override_survives_active_stage_progression_but_not_new_application(self):
        app = self.apply()
        self.decide("OVERRIDE", job_id="test:2")
        self.event(app, "INTERVIEW")
        self.assertTrue(lifecycle.consideration(self.relation(), "test:2")[0])
        self.apply("test:3")  # Explicitly record reality even if normal selection discouraged it.
        self.assertFalse(lifecycle.consideration(self.relation(), "test:2")[0])
        self.assertEqual(len(self.audit()["decisions"]), 1)

    def test_new_review_outcome_requires_new_override(self):
        app = self.apply()
        self.event(app, "SCREEN")
        self.decide("OVERRIDE", job_id="test:2")
        self.event(app, "REJECTED", reason="Synthetic rejection")
        self.assertFalse(lifecycle.consideration(self.relation(), "test:2")[0])
        self.decide("OVERRIDE", job_id="test:2")
        self.assertTrue(lifecycle.consideration(self.relation(), "test:2")[0])

    def test_changed_opportunity_content_requires_fresh_authorization(self):
        self.apply()
        self.decide("OVERRIDE", job_id="test:2")
        self.jobs[1]["description"] += " New responsibilities."
        state.record_jobs(self.db, self.jobs, TEST_REGISTRY)
        self.assertFalse(lifecycle.consideration(self.relation(), "test:2")[0])

    def test_override_requires_reason_employer_job_and_restriction(self):
        with self.assertRaises(ValueError):
            self.decide("OVERRIDE", job_id="test:2")
        self.apply()
        before = self.audit()
        for reason, job in ((None, "test:2"), (" ", "test:2"), ("reason", None), ("reason", "missing"), ("reason", "test:1")):
            with self.subTest(reason=reason, job=job), self.assertRaises(ValueError):
                self.decide("OVERRIDE", reason=reason, job_id=job)
        state.record_jobs(self.db, [fixture(id="good:9")], TEST_REGISTRY)
        with self.assertRaises(ValueError):
            self.decide("OVERRIDE", job_id="good:9")
        self.assertEqual(self.audit(), before)

    def test_multiple_applications_and_review_resolution_cannot_clear_active(self):
        first, second = self.apply(), self.apply("test:3")
        self.event(first, "INTERVIEW")
        self.event(first, "REJECTED", reason="Synthetic rejection")
        self.assertEqual(self.relation()["status"], "ACTIVE APPLICATION")
        self.decide("REVIEW_CLEARED")
        self.assertEqual(self.relation()["status"], "ACTIVE APPLICATION")
        self.event(second, "REJECTED", engagement="NO", reason="No interaction")
        self.assertEqual(self.relation()["status"], "ELIGIBLE")

    def test_new_engaged_outcome_is_not_covered_by_old_review_resolution(self):
        first = self.apply()
        self.event(first, "INTERVIEW")
        self.event(first, "REJECTED", reason="Synthetic rejection")
        self.decide("REVIEW_CLEARED")
        second = self.apply("test:2")
        self.event(second, "SCREEN")
        self.event(second, "WITHDRAWN", reason="Synthetic withdrawal")
        self.assertEqual(self.relation()["status"], "REVIEW BEFORE REAPPLYING")

    def test_lifecycle_is_authoritative_and_legacy_mark_cannot_bypass_it(self):
        app = self.apply()
        with self.assertRaises(ValueError):
            state.mark_job(self.db, "test:1", "NEW")
        with self.assertRaises(ValueError):
            self.apply()
        self.event(app, "INTERVIEW")
        before = self.audit()
        with self.assertRaises(ValueError):
            self.event(app, "REJECTED", engagement="NO", reason="Contradicts recorded interview")
        self.assertEqual(self.audit(), before)

    def test_legacy_labels_do_not_create_applications_or_allow_mark_bypass(self):
        state.mark_job(self.db, "test:1", "APPLIED")
        self.assertEqual(self.audit()["applications"], [])
        state.mark_job(self.db, "test:1", "NEW")
        self.assertEqual(self.relation()["status"], "RECONCILIATION REQUIRED")
        with self.assertRaises(ValueError):
            self.decide("OVERRIDE", job_id="test:2")
        self.assertEqual(self.scout()[0]["selection_job_ids"], [])
        self.decide("LEGACY_ELIGIBLE", job_id="test:1")
        self.assertEqual(self.relation()["status"], "ELIGIBLE")
        self.assertEqual(self.audit()["applications"], [])
        self.assertEqual(len(self.audit()["legacy_facts"]), 1)

    def test_legacy_review_and_linked_reconciliation_preserve_facts(self):
        state.mark_job(self.db, "test:1", "INTERVIEW")
        before = state.read_history(self.db)
        self.decide("LEGACY_REVIEW", job_id="test:1")
        self.assertEqual(self.relation()["status"], "REVIEW BEFORE REAPPLYING")
        self.assertEqual(state.read_history(self.db), before)
        self.decide("REVIEW_CLEARED")
        self.assertEqual(self.relation()["status"], "ELIGIBLE")
        app = self.apply()
        self.decide("LEGACY_LINKED", job_id="test:1", application_id=app)
        self.assertEqual(self.relation()["status"], "ACTIVE APPLICATION")
        self.assertEqual(self.audit()["applications"][0]["engagement"], "UNKNOWN")

    def test_cli_actions_are_explicit_and_never_fetch(self):
        code, output, _ = self.command("--record-application", "test:1", "--occurred-at", "2026-09-20")
        self.assertEqual(code, 0)
        app = str(json.loads(output)["application_id"])
        self.assertEqual(self.command("--application-event", app, "SCREEN")[0], 0)
        self.assertEqual(self.command("--authorize-opportunity", "fixture-test", "test:2")[0], 3)
        self.assertEqual(self.command("--authorize-opportunity", "fixture-test", "test:2", "--reason", "Synthetic approval")[0], 0)
        self.assertEqual(self.command("--application-event", app, "REJECTED", "--reason", "Synthetic rejection")[0], 0)
        self.assertEqual(self.command("--resolve-reapply-review", "fixture-test", "--reason", "Synthetic review complete")[0], 0)
        self.assertEqual(self.command("--applications")[0], 0)
        self.assertEqual(self.command("--employer-status", "fixture-test")[0], 0)

    def test_unused_cli_options_fail_before_mutation(self):
        before = self.audit()
        for args in (("--reason", "stray"), ("--engagement", "NO"), ("--disposition", "ELIGIBLE"), ("--occurred-at", "2026-09-20")):
            with self.subTest(args=args), self.assertRaises(SystemExit) as caught:
                self.command(*args)
            self.assertEqual(caught.exception.code, 2)
        self.assertEqual(self.audit(), before)

    def test_invalid_events_dates_and_control_codes_leave_no_partial_writes(self):
        before = self.audit()
        for date in ("yesterday", "2026-09-20T12:00:00", "2026-99-99"):
            with self.assertRaises(ValueError):
                lifecycle.record_application(self.db, "test:1", date)
        self.assertEqual(self.audit(), before)
        app = self.apply()
        for event, kwargs in (("ACCEPTED", {}), ("REJECTED", {}), ("SCREEN", {"engagement": "NO"}),
                              ("REJECTED", {"reason": "bad\x1b[2J"})):
            with self.assertRaises(ValueError):
                self.event(app, event, **kwargs)
        self.assertEqual(len(self.audit()["applications"][0]["events"]), 1)

    def test_free_text_is_sql_data_and_markdown_escaped(self):
        self.apply()
        reason = "'); DROP TABLE jobs; --\n\n# forged\n![tracker](https://example.org/x)<script>"
        self.decide("OVERRIDE", reason, "test:2")
        run, markdown = self.scout()
        self.assertNotIn("\n# forged", markdown)
        self.assertNotIn("![tracker]", markdown)
        self.assertNotIn("<script>", markdown)
        self.assertEqual(len(state.read_history(self.db)), 7)
        self.assertEqual(self.audit()["decisions"][0]["reason"], reason)
        self.assertEqual(run["selection_job_ids"], ["test:2"])

    def test_refresh_absence_and_restart_preserve_lifecycle_history(self):
        app = self.apply()
        self.event(app, "SCREEN")
        self.event(app, "WITHDRAWN", reason="Synthetic withdrawal")
        before = self.audit()
        state.record_jobs(self.db, [], TEST_REGISTRY)
        result = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("job_scout.py")),
                                 "--state-file", str(self.db), "--applications"], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), before)

    def test_lifecycle_transaction_rolls_back_after_partial_insert(self):
        real_open = lifecycle._open
        def denied_event(path):
            connection = real_open(path)
            connection.set_authorizer(lambda operation, name, *rest:
                sqlite3.SQLITE_DENY if operation == sqlite3.SQLITE_INSERT and name == "application_events"
                else sqlite3.SQLITE_OK)
            return connection
        before = state.read_history(self.db)
        with patch("application_lifecycle._open", side_effect=denied_event), self.assertRaises(sqlite3.DatabaseError):
            self.apply()
        self.assertEqual(self.audit()["applications"], [])
        self.assertEqual(state.read_history(self.db), before)


class MigrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.db = Path(temp.name) / "synthetic-v2.sqlite3"
        with closing(sqlite3.connect(self.db)) as connection, connection:
            for sql in state.V2_SCHEMA.values():
                connection.execute(sql)
            state._sync_registry(connection, TEST_REGISTRY)
            for n, status in enumerate(state.STATES):
                connection.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (f"test:{n}", status, json.dumps(fixture(id=f"test:{n}")), "first", "last", "updated", "fixture-test", "test"))
            connection.execute("INSERT INTO source_runs VALUES (1, 'test', 'observed', 1, 7, 7, NULL)")
            connection.execute("PRAGMA user_version=2")

    def rows(self, table):
        with closing(sqlite3.connect(self.db)) as connection:
            return connection.execute(f"SELECT * FROM {table}").fetchall()  # Static test-owned table names only.

    def test_v2_migration_preserves_all_values_without_inferred_applications(self):
        before = {name: self.rows(name) for name in state.V2_SCHEMA}
        state.migrate_database(self.db, TEST_REGISTRY)
        self.assertEqual({name: self.rows(name) for name in state.V2_SCHEMA}, before)
        audit = lifecycle.read_applications(self.db)
        self.assertEqual(audit["applications"], [])
        self.assertEqual(audit["decisions"], [])
        self.assertEqual({f["status"] for f in audit["legacy_facts"]}, {"APPLIED", "INTERVIEW", "OFFER", "REJECTED"})
        self.assertEqual(lifecycle.employer_relationships(self.db)["fixture-test"]["status"], "RECONCILIATION REQUIRED")
        state.migrate_database(self.db, TEST_REGISTRY)
        self.assertEqual(lifecycle.read_applications(self.db), audit)

    def test_normal_v2_access_refuses_without_mutation(self):
        before = self.db.read_bytes()
        with self.assertRaisesRegex(ValueError, "explicit migration"):
            state.read_history(self.db)
        self.assertEqual(self.db.read_bytes(), before)

    def test_v2_failure_rolls_back_ddl_facts_version_and_data(self):
        before = self.db.read_bytes()
        real = state._check_schema
        def fail(connection, schema):
            real(connection, schema)
            if "applications" in schema:
                raise sqlite3.OperationalError("Synthetic failure after schema/facts/version changes")
        with patch("application_state._check_schema", side_effect=fail), self.assertRaises(sqlite3.OperationalError):
            state.migrate_database(self.db, TEST_REGISTRY)
        self.assertEqual(self.db.read_bytes(), before)

    def test_future_version_fails_without_mutation(self):
        with closing(sqlite3.connect(self.db)) as connection:
            connection.execute("PRAGMA user_version=999")
        before = self.db.read_bytes()
        with self.assertRaises(ValueError):
            state.migrate_database(self.db, TEST_REGISTRY)
        self.assertEqual(self.db.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
