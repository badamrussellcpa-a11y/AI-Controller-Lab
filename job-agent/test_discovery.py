"""Task 3 discovery contract; every database and feed below is synthetic."""
from contextlib import closing, redirect_stdout, redirect_stderr
from copy import deepcopy
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from application_state import mark_job, read_history, STATES
from job_scout import (evaluate, load_rules, classify_location, select_discovery,
                       load_commute_preferences, main, render_report)
from test_job_scout import fixture, TEST_REGISTRY


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.db = self.folder / "state.sqlite3"
        self.registry = deepcopy(TEST_REGISTRY)
        self.weights, self.rejects = load_rules()

    def evaluate(self, title, **changes):
        return evaluate(fixture(title=title, **changes), self.weights, self.rejects)

    def run_scout(self, feeds, *args):
        config = self.folder / "employers.json"
        config.write_text(json.dumps(self.registry), encoding="utf-8")
        def fetch(board, company):
            result = feeds[board]
            if isinstance(result, Exception):
                raise result
            return [dict(job, company=company) for job in result]
        with patch("job_scout.fetch_jobs", side_effect=fetch), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            result = main(["--state-file", str(self.db), "--registry", str(config),
                           "--output", str(self.folder / "reports"), *args])
        report = sorted((self.folder / "reports").glob("discovery-*.json"))[-1]
        return result, json.loads(report.read_text(encoding="utf-8")), report.with_suffix(".md").read_text(encoding="utf-8")

    def test_primary_titles_and_variants_have_explainable_clear_classification(self):
        titles = ["Controller", "Assistant Controller", "Corporate Controller", "Financial Controller",
                  "Accounting Manager", "Manager, Accounting", "Corporate Accounting Manager",
                  "Technical Accounting Manager", "Sr. Accounting Manager", "Senior Manager, Accounting",
                  "Manager, Technical Accounting", "Senior Manager of Accounting", "Senior Accountant",
                  "Sr. Accountant", "Senior Corporate Accountant"]
        for title in titles:
            with self.subTest(title=title):
                job = self.evaluate(title)
                self.assertIsNotNone(job)
                self.assertEqual(job["review_status"], "CLEAR MATCH")
                self.assertIn("Primary role family:", job["classification_reason"])

    def test_adjacent_senior_families_are_review_needed(self):
        titles = ["Manager, FP&A", "Senior FP&A Analyst", "Director, Financial Planning & Analysis",
                  "Treasury Manager", "Tax Manager", "Senior Tax Accountant", "Internal Audit Manager",
                  "Payroll Manager", "AP Manager", "AR Manager", "Accounts Payable Supervisor",
                  "Director of Accounts Receivable", "VP Finance", "Chief Financial Officer",
                  "CFO", "Senior Financial Analyst", "Director of Accounting",
                  "Credit Manager", "Manager, Accounting Operations"]
        for title in titles:
            with self.subTest(title=title):
                job = self.evaluate(title)
                self.assertIsNotNone(job)
                self.assertEqual(job["review_status"], "REVIEW NEEDED")
                self.assertTrue(job["classification_reason"])

    def test_false_positives_and_junior_roles_stay_excluded(self):
        titles = ["Software Controller", "Hardware Controller", "Document Controller", "Flight Controller",
                  "Air Traffic Controller", "Inventory Controller", "Lead Hardware Engineer (Controllers)",
                  "Auto Finance Manager", "Finance Manager — Auto Lending", "Consumer-Lending Finance Manager",
                  "Mortgage Finance Manager", "Loan Officer", "Loan Origination Manager",
                  "Insurance Sales Finance Director", "Finance & Insurance Manager",
                  "Accounting Clerk", "AP Clerk", "AR Clerk", "Bookkeeper", "Junior Accountant",
                  "Entry-Level Accountant", "Accounting Assistant", "Staff Accountant",
                  "Finance Intern", "Financial Advisor", "Senior Financial Planner",
                  "Product Manager, Finance", "Quality Audit Manager", "Treasury Analyst",
                  "Payroll Specialist", "Sales Manager - Finance"]
        for title in titles:
            with self.subTest(title=title):
                self.assertIsNone(self.evaluate(title))  # Even with accounting-keyword fixture text.

    def test_finance_manager_scope_is_not_weighted_coverage(self):
        job = self.evaluate("Finance Manager", description="Own budgeting and forecasting.")
        self.assertEqual(job["review_status"], "REVIEW NEEDED")
        self.assertEqual(job["accounting_signal_coverage"], 0)
        self.assertIn("responsibility evidence", job["classification_reason"])
        self.assertIsNone(self.evaluate("Finance Manager", description="Sell consumer loans and vehicle warranties."))
        missing = self.evaluate("Finance Manager", description="")
        self.assertEqual(missing["review_status"], "REVIEW NEEDED")
        self.assertIn("missing", missing["classification_reason"])

    def test_description_topic_mention_flags_without_claiming_occupation(self):
        job = self.evaluate("Accounting Manager", description="Monthly close; no mortgage experience required.")
        self.assertEqual(job["review_status"], "REVIEW NEEDED")
        self.assertTrue(any("mortgage" in w for w in job["warnings"]))

    def test_seven_jobs_at_one_employer_are_untruncated_in_both_formats(self):
        jobs = [fixture(id=f"test:{n}", description="Responsibilities available on request.") for n in range(7)]
        result, run, markdown = self.run_scout({"test": jobs, "good": [], "bad": []})
        self.assertEqual(result, 0)
        self.assertEqual(len(run["jobs"]), 7)
        self.assertEqual(len(run["fresh_job_ids"]), 7)
        self.assertTrue(all(j["accounting_signal_coverage"] == 0 for j in run["jobs"]))
        self.assertEqual(markdown.count("### Senior Accountant"), 7)
        self.assertNotIn("Top 5", markdown)
        self.assertTrue(run["coverage_complete"])

    def test_canonical_employer_grouping_and_deterministic_order_not_coverage(self):
        # One employer has two explicit boards; same display names do not merge employers.
        self.registry["employers"][0]["greenhouse_boards"].append("second")
        self.registry["employers"][0]["display_name"] = "Same Name"
        self.registry["employers"][1]["display_name"] = "Same Name"
        test_jobs = [fixture(id="test:3", title="Senior Accountant", description="Month-end close. General ledger. Financial reporting."),
                     fixture(id="test:2", title="Payroll Manager"),
                     fixture(id="test:1", title="Controller", description="Responsibilities available on request.")]
        feeds = {"test": test_jobs, "second": [fixture(id="second:4", title="Accounting Manager")],
                 "good": [fixture(id="good:5")], "bad": []}
        _, run, markdown = self.run_scout(feeds)
        test_ids = [j["id"] for j in run["jobs"] if j["employer_id"] == "fixture-test"]
        self.assertEqual(test_ids, ["test:1", "second:4", "test:3", "test:2"])
        self.assertEqual(markdown.count("## Same Name\n"), 2)
        self.assertEqual(markdown.count("Employer ID: fixture\\-test"), 1)
        feeds["test"] = list(reversed(test_jobs))
        _, again, _ = self.run_scout(feeds)
        self.assertEqual([j["id"] for j in run["jobs"]], [j["id"] for j in again["jobs"]])

    def test_swapping_coverage_and_pay_does_not_change_order(self):
        low = self.evaluate("Controller", id="test:1", description="Responsibilities available. Pay $1.")
        high = self.evaluate("Senior Accountant", id="test:2", description="Month-end close. General ledger. Pay $900,000.")
        settings = load_commute_preferences()
        selected = select_discovery([high, low], settings, {})
        self.assertEqual([j["id"] for j in selected], ["test:1", "test:2"])
        low["accounting_signal_coverage"], high["accounting_signal_coverage"] = 100, 0
        self.assertEqual([j["id"] for j in select_discovery([high, low], settings, {})], ["test:1", "test:2"])

    def test_retired_limit_fails_before_state_or_network(self):
        for args in (["--limit", "5"], ["--limit=20"], ["--limit"], ["--limit", "garbage"]):
            errors = io.StringIO()
            with self.subTest(args=args), patch("job_scout.fetch_jobs") as fetch, redirect_stderr(errors):
                with self.assertRaises(SystemExit) as raised:
                    main(["--state-file", str(self.db), *args])
                self.assertEqual(raised.exception.code, 2)
                self.assertIn("--limit is retired", errors.getvalue())
                fetch.assert_not_called()
                self.assertFalse(self.db.exists())

    def test_location_compatible_cases(self):
        for location in ["Los Angeles, CA", "Hybrid - El Segundo, CA", "Remote - California",
                         "Remote - CA", "Remote - anywhere in the United States", "Remote (all 50 states)"]:
            with self.subTest(location=location):
                job = self.evaluate("Controller", location=location)
                self.assertEqual(job["location_classification"], "COMPATIBLE")
                self.assertEqual(job["review_status"], "CLEAR MATCH")

    def test_ambiguous_locations_are_review_needed_not_hidden(self):
        locations = ["", "Unrecognized City", "Remote", "Remote - US", "Hybrid", "San Francisco, CA",
                     "Remote - Canada (CA)", "Remote - CA / NY"]
        for location in locations:
            with self.subTest(location=location):
                job = self.evaluate("Controller", location=location)
                self.assertEqual(job["location_classification"], "REVIEW NEEDED")
                self.assertEqual(job["review_status"], "REVIEW NEEDED")
                self.assertIn("LOCATION", " ".join(job["warnings"]))
        _, run, _ = self.run_scout({"test": [fixture(id=f"test:{n}", location=loc) for n, loc in enumerate(locations)],
                                   "good": [], "bad": []})
        self.assertEqual(len(run["jobs"]), len(locations))

    def test_explicit_incompatible_geography_is_retained_and_inspectable(self):
        for location in ["Austin, TX", "Glendale, AZ", "Remote - UK", "Remote - Texas",
                         "Remote - US excluding CA", "Remote (California excluded)",
                         "Remote - US not California", "Remote excluding residents of CA"]:
            with self.subTest(location=location):
                self.assertEqual(classify_location(location)[0], "INCOMPATIBLE")
        feeds = {"test": [fixture(location="Austin, TX")], "good": [], "bad": []}
        _, run, _ = self.run_scout(feeds)
        self.assertEqual(run["jobs"], [])
        self.assertEqual(run["excluded_location_count"], 1)
        self.assertEqual(len(read_history(self.db)), 1)
        _, all_locations, markdown = self.run_scout(feeds, "--all-locations")
        self.assertEqual(len(all_locations["jobs"]), 1)
        self.assertEqual(all_locations["fresh_job_ids"], [])
        self.assertIn("outside\\-area", markdown)

    def test_location_review_does_not_fabricate_commute(self):
        job = self.evaluate("Controller", location="New City")
        selected = select_discovery([job], load_commute_preferences(), {})
        self.assertFalse(selected[0]["commute"]["destination_confirmed"])
        self.assertEqual(selected[0]["commute"]["bucket"], "Commute unverified")

    def test_all_saved_states_remain_visible_but_handled_jobs_are_not_fresh(self):
        jobs = [fixture(id=f"test:{n}") for n in range(len(STATES))]
        feeds = {"test": jobs, "good": [], "bad": []}
        self.run_scout(feeds)
        for job, status in zip(jobs, STATES):
            mark_job(self.db, job["id"], status)
        original = {row["id"]: row for row in read_history(self.db)}
        _, run, markdown = self.run_scout(feeds)
        self.assertEqual([j["application_status"] for j in run["jobs"]], list(STATES))
        self.assertEqual(run["fresh_job_ids"], ["test:0", "test:1"])
        self.assertEqual(markdown.count("Handled state — not a fresh application recommendation."), 5)
        self.assertEqual(len(run["jobs"]), 7)  # No employer suppression.
        for row in read_history(self.db):
            self.assertEqual(row["first_seen"], original[row["id"]]["first_seen"])
            self.assertEqual(row["status_updated_at"], original[row["id"]]["status_updated_at"])
        self.run_scout({"test": [], "good": [], "bad": []})
        self.assertEqual(len(read_history(self.db)), 7)

    def test_partial_failure_is_incomplete_and_not_zero_yield(self):
        result, run, markdown = self.run_scout({"test": [fixture()], "good": [], "bad": OSError("offline")})
        self.assertEqual(result, 2)
        self.assertFalse(run["coverage_complete"])
        self.assertIn("Source coverage: INCOMPLETE", markdown)
        self.assertIn("0 recognized accounting/finance roles", markdown)
        self.assertIn("FAILED", markdown)
        with closing(sqlite3.connect(self.db)) as connection:
            rows = connection.execute("SELECT board, success, fetched_count, relevant_count FROM source_runs").fetchall()
        self.assertEqual(rows, [("test", 1, 1, 1), ("good", 1, 0, 0), ("bad", 0, None, None)])

    def test_board_subset_does_not_claim_all_active_coverage(self):
        _, run, markdown = self.run_scout({"test": [fixture()]}, "--boards", "test")
        self.assertFalse(run["coverage_complete"])
        self.assertIn("Selected source boards: 1 of 3 ACTIVE boards.", markdown)
        self.assertIn("INCOMPLETE", markdown)

    def test_bench_paused_never_fetched_and_zero_employers_are_reported(self):
        self.registry["employers"][1]["pool"] = "BENCH"
        self.registry["employers"][2]["pool"] = "PAUSED"
        _, run, markdown = self.run_scout({"test": []})
        self.assertEqual(run["active_employer_count"], 1)
        self.assertEqual([s["board"] for s in run["sources"]], ["test"])
        self.assertIn("## Test", markdown)
        self.assertIn("No displayed roles", markdown)
        self.assertTrue(run["coverage_complete"])

    def test_observed_relevant_counts_use_broader_policy_before_geography(self):
        jobs = [fixture(title="Payroll Manager"), fixture(id="test:2", title="Manager, FP&A", location="Austin, TX"),
                fixture(id="test:3", title="Accounting Clerk")]
        _, run, _ = self.run_scout({"test": jobs, "good": [], "bad": []})
        self.assertEqual(run["target_count"], 2)
        self.assertEqual(len(run["jobs"]), 1)
        with closing(sqlite3.connect(self.db)) as connection:
            self.assertEqual(connection.execute("SELECT relevant_count FROM source_runs WHERE board='test'").fetchone(), (2,))
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone(), (3,))

    def test_new_heading_and_context_fields_cannot_inject_markdown(self):
        payload = "\n\n# forged\n![tracker](https://example.org/x)<script>x</script>\\\\"
        job = self.evaluate("Senior Accountant" + payload, location="Unknown" + payload)
        job["company"] = "Employer" + payload
        job["classification_reason"] += payload
        job["location_review"] += payload
        job["warnings"].append(payload)
        markdown = render_report({"retrieved_at": "test", "sources": [], "fetched_count": 1,
                                  "target_count": 1, "jobs": [job]})
        self.assertNotIn("\n# forged", markdown)
        self.assertNotIn("<script>", markdown)
        self.assertNotIn("![tracker](", markdown)
        self.assertIn("\\# forged", markdown)
        self.assertIn("&lt;script&gt;", markdown)
        self.assertEqual(sum(line.startswith("### ") for line in markdown.splitlines()), 1)

    def test_classification_and_unknown_pay_persist_as_facts(self):
        _, run, _ = self.run_scout({"test": [fixture(title="Treasury Manager", description="Cash management.")],
                                   "good": [], "bad": []})
        job = read_history(self.db)[0]["job"]
        self.assertEqual(job["review_status"], "REVIEW NEEDED")
        self.assertEqual(job["salary_excerpts"], [])
        self.assertTrue(job["classification_reason"])
        self.assertEqual(job["accounting_signal_coverage"], 0)
        self.assertNotIn("score", run["jobs"][0])


if __name__ == "__main__":
    unittest.main()
