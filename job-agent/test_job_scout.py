import json
from datetime import date
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from job_scout import evaluate, load_rules, location_status, main, role_for, salary_evidence
from scraper import plain_text
from job_scout import assess_commute, select_shortlist
from urllib.parse import parse_qs, urlparse


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
