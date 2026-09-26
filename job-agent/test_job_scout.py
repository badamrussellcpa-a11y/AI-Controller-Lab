import json
from datetime import date
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout
import io
import subprocess
import sys
from unittest.mock import patch
from job_scout import evaluate, load_rules, location_status, main as scout_main, role_for, salary_evidence
from application_state import STATES, FRESH_STATES, mark_job, read_history, record_jobs
from scraper import fetch_jobs, plain_text, validate_application_url
from job_scout import assess_commute, render_report, select_shortlist
from urllib.parse import parse_qs, urlparse


def main(argv):
    # Existing search tests also get isolated persistent state, never the user's DB.
    if "--state-file" not in argv:
        folder = Path(argv[argv.index("--output") + 1])
        argv = [*argv, "--state-file", str(folder / "state.sqlite3")]
    return scout_main(argv)


def fixture(**changes):
    return {"id": "test:1", "company": "Test", "title": "Senior Accountant",
            "location": "Long Beach, CA", "description": "Month-end close and general ledger. Journal entries.",
            "url": "https://example.com/jobs/1", "source": "fixture", "updated_at": "", **changes}


class ScoutTests(unittest.TestCase):
    def setUp(self):
        self.weights, self.rejects = load_rules()

    def test_html_entities(self):
        self.assertEqual(plain_text("&lt;p&gt;Close &amp;amp; reporting&lt;/p&gt;"), "Close & reporting")

    def test_false_title(self):
        self.assertIsNone(role_for("Lead Hardware Engineer (Controllers)"))
        self.assertIsNone(role_for("Document Controller"))

    def test_accounting_titles(self):
        self.assertEqual(role_for("Assistant Controller"), "Assistant Controller")
        self.assertEqual(role_for("Sr. Accountant"), "Senior Accountant")

    def test_score_counts_signal_once(self):
        result = evaluate(fixture(description="month-end close month-end close"), self.weights, self.rejects)
        self.assertEqual(result["score"], round(100*10/sum(self.weights.values())))

    def test_missing_salary_is_unknown(self):
        self.assertEqual(evaluate(fixture(), self.weights, self.rejects)["salary_excerpts"], [])

    def test_pay_range_is_not_duplicated(self):
        self.assertEqual(len(salary_evidence("Base salary $100,000 - $120,000 per year.")), 1)

    def test_finance_manager_requires_leadership_and_accounting(self):
        self.assertIsNone(evaluate(fixture(title="Finance Manager"), self.weights, self.rejects))
        self.assertIsNotNone(evaluate(fixture(title="Finance Manager", description="Lead a team and own financial reporting."), self.weights, self.rejects))

    def test_topic_mention_review(self):
        result = evaluate(fixture(description="Month-end close. No mortgage experience required."), self.weights, self.rejects)
        self.assertEqual(result["review_status"], "REVIEW")

    def test_rejected_title(self):
        self.assertIsNone(evaluate(fixture(title="Controller - Auto Finance"), self.weights, self.rejects))

    def test_remote_not_eligibility_promise(self):
        self.assertIn("verify California", location_status("Remote - UK"))

    def test_partial_failure_and_duplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch("job_scout.fetch_jobs", side_effect=[[fixture(), fixture()], OSError("offline")]):
                self.assertEqual(main(["--boards", "good", "bad", "--output", folder]), 2)
            report = json.loads(next(Path(folder).glob("*.json")).read_text(encoding="utf-8"))
            self.assertEqual(len(report["jobs"]), 1)
            self.assertEqual(len(report["sources"]), 2)

    def test_all_failed_not_success(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch("job_scout.fetch_jobs", side_effect=OSError("offline")):
                self.assertEqual(main(["--boards", "bad", "--output", folder]), 1)

    def test_out_of_area_filtered(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch("job_scout.fetch_jobs", return_value=[fixture(location="Austin, TX")]):
                self.assertEqual(main(["--boards", "test", "--output", folder]), 0)
            report = json.loads(next(Path(folder).glob("*.json")).read_text(encoding="utf-8"))
            self.assertEqual(report["jobs"], [])


class ApplicationUrlTests(unittest.TestCase):
    def report(self, url):
        weights, rejects = load_rules()
        return render_report({"retrieved_at": "test", "sources": [], "fetched_count": 1,
                              "target_count": 1, "jobs": [evaluate(fixture(url=url), weights, rejects)]})

    def feed(self, url):
        return {"jobs": [{"id": 123, "title": "Senior Accountant", "absolute_url": url,
                          "location": {"name": "Long Beach, CA"}, "content": "Month-end close"}]}

    def test_valid_source_urls_preserved(self):
        urls = ["https://boards.greenhouse.io/example/jobs/123?gh_src=a%2Fb#app",
                "https://job-boards.greenhouse.io/example/jobs/123",
                "https://careers.example.com/openings?gh_jid=123&gh_src=abc",
                "http://careers.example.com:8080/jobs/123",
                "https://careers.example.com/jobs/Accountant_(Senior)",
                "https://[2001:db8::1]/jobs/123"]
        for url in urls:
            with self.subTest(url=url), patch("scraper.urlopen", return_value=io.StringIO(json.dumps(self.feed(url)))):
                self.assertEqual(validate_application_url(url), url)
                self.assertEqual(fetch_jobs("test", "Test")[0]["url"], url)
                self.assertIn("Application: <" + url.replace("&", "&amp;") + ">", self.report(url))

    def test_invalid_values_rejected_at_import_and_output(self):
        urls = [None, 42, True, ["https://example.com"], {"url": "https://example.com"}, "",
                "javascript:alert(1)", "data:text/html,test", "file:///C:/test", "ftp://example.com/a",
                "//example.com/a", "/jobs/1", "https:///missing", "https://", "https://bad host/a",
                " https://example.com/a", "https://user:secret@example.com/a", "https://example.com:abc/a",
                "https://example.com:65536/a", "https://example.com:/a", "https://[broken/a",
                "https://example..com/a", "https://-bad.example/a", "https://example.com\\@evil.example/a",
                "https://example.com/%zz", "https://example.com/%0a%23injected",
                "https://example.com/a\n\n# injected", "https://example.com/a\r\n![image](https://example.org/x)",
                "https://example.com/a\t", "https://example.com/a\x00", "https://example.com/a\x1b",
                "https://example.com/a\x7f", "https://example.com/a\u0085", "https://example.com/a\u2028",
                "https://example.com/a\u202e"]
        for url in urls:
            with self.subTest(url=repr(url)):
                with self.assertRaises(ValueError):
                    validate_application_url(url)
                with patch("scraper.urlopen", return_value=io.StringIO(json.dumps(self.feed(url)))):
                    with self.assertRaises(ValueError):
                        fetch_jobs("test", "Test")
                with self.assertRaises(ValueError):
                    self.report(url)

    def test_markdown_delimiters_and_entities_cannot_escape_autolink(self):
        url = 'https://example.com/jobs/1><img/src=x>?q=[label](target)&copy;="value"#`code`'
        report = self.report(url)
        line = next(line for line in report.splitlines() if line.startswith("Application:"))
        self.assertEqual(line, 'Application: <https://example.com/jobs/1%3E%3Cimg/src=x%3E?q=[label](target)&amp;copy;=%22value%22#%60code%60>')
        self.assertEqual(line.count("<"), 1)
        self.assertEqual(line.count(">"), 1)
        self.assertEqual(validate_application_url(url), url)

    def test_unsafe_feed_fails_without_payload_or_state_and_other_feed_continues(self):
        unsafe = "https://example.com/a\n\n# injected-secret"
        responses = [io.StringIO(json.dumps(self.feed(unsafe))),
                     io.StringIO(json.dumps(self.feed("https://example.com/jobs/123")))]
        with tempfile.TemporaryDirectory() as folder, patch("scraper.urlopen", side_effect=responses):
            with patch("sys.stderr", new_callable=io.StringIO) as errors:
                self.assertEqual(main(["--boards", "bad", "good", "--output", folder]), 2)
                self.assertNotIn("injected-secret", errors.getvalue())
            report = json.loads(next(Path(folder).glob("shortlist-*.json")).read_text(encoding="utf-8"))
            self.assertEqual([j["id"] for j in report["jobs"]], ["good:123"])
            self.assertNotIn("injected-secret", json.dumps(report))
            self.assertEqual([j["id"] for j in read_history(Path(folder) / "state.sqlite3")], ["good:123"])


class ApplicationStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.state = self.folder / "state.sqlite3"
        self.args = ["--state-file", str(self.state)]

    def search(self, jobs, *extra):
        with patch("job_scout.fetch_jobs", return_value=jobs):
            self.assertEqual(scout_main([*self.args, "--boards", "test", "--output",
                                         str(self.folder), *extra]), 0)
        return json.loads(sorted(self.folder.glob("shortlist-*.json"))[-1].read_text(encoding="utf-8"))

    def test_all_states_persist_and_filter_before_limit(self):
        jobs = [fixture(id=f"test:{n}") for n in range(9)]
        self.search(jobs)
        for job, status in zip(jobs, STATES):
            self.assertEqual(scout_main([*self.args, "--mark", job["id"], status]), 0)
        run = self.search(jobs, "--all-locations", "--limit", "3")
        expected = [j["id"] for j, state in zip(jobs, STATES) if state in FRESH_STATES] + ["test:7"]
        self.assertEqual([j["id"] for j in run["jobs"]], expected)
        self.assertEqual({r["id"]: r["status"] for r in read_history(self.state)},
                         {j["id"]: STATES[n] if n < len(STATES) else "NEW" for n, j in enumerate(jobs)})

    def test_absent_jobs_and_first_seen_preserved(self):
        self.search([fixture()])
        mark_job(self.state, "test:1", "APPLIED")
        original = read_history(self.state)[0]
        self.search([])
        self.assertEqual(read_history(self.state)[0], original)
        run = self.search([fixture(title="Senior Accountant II")])
        updated = read_history(self.state)[0]
        self.assertEqual(run["jobs"], [])
        self.assertEqual(updated["first_seen"], original["first_seen"])
        self.assertEqual(updated["status_updated_at"], original["status_updated_at"])
        self.assertEqual(updated["job"]["title"], "Senior Accountant II")
        self.assertGreaterEqual(updated["last_seen"], original["last_seen"])

    def test_failure_keeps_records_and_status(self):
        self.search([fixture()])
        mark_job(self.state, "test:1", "APPLIED")
        before = read_history(self.state)
        with patch("job_scout.fetch_jobs", side_effect=OSError("offline")):
            self.assertEqual(scout_main([*self.args, "--boards", "test", "--output", str(self.folder)]), 1)
        self.assertEqual(read_history(self.state), before)

    def test_mark_validation_history_and_reopen_without_fetch(self):
        record_jobs(self.state, [fixture()])
        with patch("job_scout.fetch_jobs") as fetch:
            for job_id, status in [("test:1", "INVALID"), ("missing", "APPLIED")]:
                self.assertEqual(scout_main([*self.args, "--mark", job_id, status]), 3)
            self.assertEqual(scout_main([*self.args, "--mark", "test:1", "APPLIED"]), 0)
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(scout_main([*self.args, "--history"]), 0)
            self.assertEqual(json.loads(output.getvalue())[0]["status"], "APPLIED")
            self.assertEqual(scout_main([*self.args, "--mark", "test:1", "NEW"]), 0)
            fetch.assert_not_called()
        self.assertEqual(len(self.search([fixture()])["jobs"]), 1)

    def test_bad_state_stops_without_fetch_or_report(self):
        self.state.write_bytes(b"not a SQLite database")
        with patch("job_scout.fetch_jobs") as fetch:
            self.assertEqual(scout_main([*self.args, "--output", str(self.folder)]), 3)
            fetch.assert_not_called()
        self.assertEqual(self.state.read_bytes(), b"not a SQLite database")
        self.assertEqual(list(self.folder.glob("shortlist-*")), [])

    def test_history_survives_windows_console_encoding(self):
        record_jobs(self.state, [fixture(description="Non\u2011breaking hyphen and \u5de5\u4f5c")])
        output = io.BytesIO()
        stream = io.TextIOWrapper(output, encoding="cp1252")
        with redirect_stdout(stream):
            self.assertEqual(scout_main([*self.args, "--history"]), 0)
        stream.flush()
        self.assertEqual(json.loads(output.getvalue())[0]["job"]["description"],
                         "Non\u2011breaking hyphen and \u5de5\u4f5c")

    def test_transaction_rolls_back_on_invalid_record(self):
        record_jobs(self.state, [fixture()])
        with self.assertRaises(KeyError):
            record_jobs(self.state, [fixture(id="test:2"), {}])
        self.assertEqual([r["id"] for r in read_history(self.state)], ["test:1"])

    def test_acceptance_across_processes(self):
        # Real CLI/state/report pipeline; only public network input is substituted.
        script = ("import sys; from unittest.mock import patch; "
                  "from test_job_scout import fixture; from job_scout import main; "
                  "jobs=[fixture(id=f'test:{n}') for n in range(6)]; "
                  "p=patch('job_scout.fetch_jobs', return_value=jobs); p.start(); "
                  "raise SystemExit(main(sys.argv[1:]))")
        base = [sys.executable, "-c", script, *self.args]
        def invoke(*args):
            result = subprocess.run([*base, *args], cwd=Path(__file__).parent,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
        first = self.folder / "first"
        second = self.folder / "second"
        invoke("--boards", "test", "--output", str(first))
        first_run = json.loads(next(first.glob("*.json")).read_text(encoding="utf-8"))
        chosen = first_run["jobs"][0]["id"]
        self.assertEqual(len(first_run["jobs"]), 5)
        invoke("--mark", chosen, "APPLIED")
        invoke("--boards", "test", "--output", str(second))
        rerun = json.loads(next(second.glob("*.json")).read_text(encoding="utf-8"))
        self.assertEqual(len(rerun["jobs"]), 5)
        self.assertNotIn(chosen, [j["id"] for j in rerun["jobs"]])
        history = read_history(self.state)
        self.assertEqual(len(history), 6)
        self.assertEqual(next(r for r in history if r["id"] == chosen)["status"], "APPLIED")


class CommuteTests(unittest.TestCase):
    def setUp(self):
        self.settings = {"commute_origin": "Hollywood Blvd and N Vista St, Los Angeles, CA",
                         "commute_mode": "driving", "commute_max_minutes": 45}
        self.review = {"origin": self.settings["commute_origin"], "mode": "driving",
                       "listing_location": "Long Beach, CA", "office_address": "Example office address",
                       "checked_on": "2026-09-25", "outbound_minutes": 40, "return_minutes": 45,
                       "arrival_time": "Weekdays 9am", "leave_work_time": "Weekdays 5pm"}

    def assess(self, review=None, **changes):
        reviews = {} if review is None else {"test:1": review}
        return assess_commute(fixture(**changes), self.settings, reviews, date(2026, 9, 25))

    def test_city_does_not_establish_time(self):
        self.assertEqual(self.assess()["bucket"], "Commute unverified")

    def test_both_directions_at_target_count(self):
        self.assertEqual(self.assess(self.review)["bucket"], "Practical now — route checked")

    def test_return_over_limit_is_stretch(self):
        self.assertEqual(self.assess({**self.review, "return_minutes": 46})["bucket"], "Stretch — over commute target")

    def test_unusable_reviews_remain_unverified(self):
        for change in [{"return_minutes": None}, {"return_minutes": True}, {"return_minutes": float("nan")},
                       {"origin": "Old apartment"}, {"mode": "transit"}, {"checked_on": "2026-07-01"},
                       {"checked_on": "2026-10-01"}, {"arrival_time": ""}, {"office_address": ""}]:
            with self.subTest(change=change):
                self.assertEqual(self.assess({**self.review, **change})["bucket"], "Commute unverified")

    def test_changed_worksite_invalidates_review(self):
        self.assertEqual(self.assess(self.review, location="Hawthorne, CA")["bucket"], "Commute unverified")

    def test_remote_requires_eligibility_review(self):
        self.assertEqual(self.assess(location="Remote - UK")["bucket"], "Remote — eligibility unverified")

    def test_route_links_reverse_directions(self):
        commute = self.assess(self.review)
        outbound = parse_qs(urlparse(commute["outbound_url"]).query)
        inbound = parse_qs(urlparse(commute["return_url"]).query)
        self.assertEqual(outbound["origin"], inbound["destination"])
        self.assertEqual(outbound["destination"], inbound["origin"])
        self.assertEqual(outbound["travelmode"], ["driving"])

    def test_commute_does_not_displace_higher_scoring_job(self):
        weights, rejects = load_rules()
        practical = evaluate(fixture(id="practical", description="journal entries"), weights, rejects)
        unknown = evaluate(fixture(), weights, rejects)
        current_review = {**self.review, "checked_on": date.today().isoformat()}
        selected = select_shortlist([unknown, practical], self.settings, {"practical": current_review}, 1)
        self.assertEqual(selected[0]["id"], "test:1")

    def test_default_five_without_commute_quota(self):
        jobs = [fixture(id=f"test:{n}") for n in range(7)]
        with tempfile.TemporaryDirectory() as folder:
            with patch("job_scout.fetch_jobs", return_value=jobs):
                self.assertEqual(main(["--boards", "test", "--output", folder]), 0)
            report = json.loads(next(Path(folder).glob("*.json")).read_text(encoding="utf-8"))
            self.assertEqual(len(report["jobs"]), 5)
            rendered = next(Path(folder).glob("*.md")).read_text(encoding="utf-8")
            self.assertNotIn("Shortfall", rendered)
            self.assertNotIn("## Commute unverified", rendered)


if __name__ == "__main__":
    unittest.main()
