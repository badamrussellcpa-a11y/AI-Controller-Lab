
"""Discover accounting/finance opportunities with factual evidence, without paid AI calls."""
import argparse
from datetime import datetime, timezone
import json
import html
from pathlib import Path
import re
import sys
import sqlite3
from application_state import DEFAULT_PATH, FRESH_STATES, STATES, mark_job, read_history, record_jobs, migrate_database
from application_lifecycle import (record_application, record_event, read_applications,
                                   employer_relationships, consideration, decide)
from employer_registry import DEFAULT_REGISTRY, load_registry, select_sources
from urllib.error import URLError
from urllib.parse import quote, urlencode
from scraper import fetch_jobs, validate_application_url

ROOT = Path(__file__).resolve().parent
PATTERNS = {
    "Month-end close": r"\bmonth[ -]end\b|\bmonthly clos(?:e|ing)\b",
    "General ledger ownership": r"\bgeneral ledger\b|\bGL\b",
    "Financial reporting": r"\bfinancial (?:reporting|statements)\b",
    "Balance sheet reconciliations": r"\bbalance sheet\b.{0,70}\breconcil|\breconcil\w*\b.{0,70}\bbalance sheet\b",
    "Journal entries": r"\bjournal entr(?:y|ies)\b",
    "Audit support": r"\baudit(?:s|ing)?\b",
    "Fixed assets": r"\bfixed assets?\b",
    "Intercompany": r"\bintercompany\b|\binter-company\b",
    "ERP systems": r"\b(?:ERP|NetSuite|SAP|Oracle|QuickBooks)\b",
    "Team leadership": r"\b(?:lead|manage|mentor|supervise)\w*\b.{0,45}\b(?:team|staff|accountants)\b|\bteam leadership\b",
}
# Ordered families are a display policy, never a score/fit ranking.
ROLES = [
    ("Assistant Controller", r"\bassistant (?:corporate )?controller\b"),
    ("Controller", r"\b(?:controller|comptroller)\b"),
    ("Accounting Manager", r"\baccounting (?:senior )?manager\b|\bmanager(?:[, /-]+| of )(?:(?:technical|corporate|financial|revenue|cost|international) )?accounting\b"),
    ("Senior Accountant", r"\b(?:senior|sr\.?) (?:corporate |technical |revenue |cost )?accountant\b"),
    ("Finance Manager", r"\b(?:finance|financial) manager\b|\bmanager[, /-]+(?:corporate )?finance\b"),
]
ADJACENT_ROLES = [
    ("FP&A", r"\bfp\s*&\s*a\b|\bfinancial planning (?:&|and) analysis\b"),
    ("Treasury", r"\btreasury\b"),
    ("Tax", r"\btax\b"),
    ("Audit", r"\b(?:internal )?audit\b"),
    ("Payroll", r"\bpayroll\b"),
    ("Accounts Payable", r"\baccounts payable\b|\ba/?p\b"),
    ("Accounts Receivable", r"\baccounts receivable\b|\ba/?r\b"),
    ("Credit / Accounting Operations", r"\bcredit\b|\b(?:accounting|finance|financial) operations\b"),
    ("Finance Leadership", r"\b(?:finance|financial|accounting|cfo)\b"),
]
PRIORITY = {role: index for index, role in enumerate([
    "Controller", "Assistant Controller", "Accounting Manager", "Senior Accountant",
    "Finance Manager", *[name for name, _ in ADJACENT_ROLES]])}
SENIORITY = r"\b(?:manager|director|head|chief|cfo|vp|vice president|senior|sr\.?|lead|supervisor)\b"
FINANCE_SCOPE = (r"\b(?:accounting|general ledger|financial (?:reporting|statements|analysis|planning)|"
                 r"month[ -]end|budget\w*|forecast\w*|treasury|cash (?:flow|management)|"
                 r"accounts (?:payable|receivable)|credit (?:risk|analysis)|fp\s*&\s*a)\b")


def load_rules(path=ROOT / "search_rules.md"):
    text = path.read_text(encoding="utf-8-sig")
    weights = {name.strip(): int(points) for name, points in
               re.findall(r"\|\s*([^|\n]+?)\s*\|\s*\+(\d+)\s*\|", text)}
    if set(weights) != set(PATTERNS) or sum(weights.values()) == 0:
        raise ValueError("Scoring table differs from supported signals; update patterns alongside rules")
    section = text.split("## Automatic Reject", 1)[1].split("\n## ", 1)[0]
    return weights, [word.strip().lower() for word in re.findall(r"^- (.+)$", section, re.MULTILINE)]


def role_for(title):
    """Identify a supported family from the title, without looking at pay/coverage."""
    title = re.sub(r"[\u2010-\u2015]", "-", title)
    if re.search(r"\b(?:engineer|developer|technician|bookkeeper|clerk|junior|intern|internship)\b"
                 r"|\bentry[ -]level\b|\bstaff accountant\b|\baccounting assistant\b"
                 r"|\b(?:software|hardware|document|flight|traffic|mission|production|quality)[ -]+controllers?\b"
                 r"|\b(?:quality|safety|security|clinical) audit\b"
                 r"|\b(?:product|project|program|sales|marketing|customer success|business development) (?:manager|director)\b"
                 r"|\bfinancial (?:advisor|adviser|planner)\b", title, re.I):
        return None
    if re.search(r"\binventory controller\b", title, re.I) and not re.search(r"\b(?:accounting|financial)\b", title, re.I):
        return None
    if re.search(SENIORITY, title, re.I) and re.search(r"\b(?:accounting|finance|financial) operations\b", title, re.I):
        return "Credit / Accounting Operations"
    for role, pattern in ROLES:
        if re.search(pattern, title, re.I):
            return role
    if re.search(SENIORITY, title, re.I):
        for role, pattern in ADJACENT_ROLES:
            if re.search(pattern, title, re.I):
                return role
    return None


def classify_role(title, description, rejects):
    role = role_for(title)
    reject_title = " ".join(re.sub(r"[-\u2010-\u2015]", " ", title).split())
    if (not role or any(re.search(r"\b" + re.escape(term.replace("-", " ")) + r"\b", reject_title, re.I) for term in rejects)
            or re.search(r"\bfinance\s*(?:&|and)\s*insurance\b", title, re.I)):
        return None
    if role in {"Finance Manager", "Credit / Accounting Operations"}:
        # This is a scope check, independent of the weighted coverage vocabulary.
        if description.strip() and not re.search(FINANCE_SCOPE, description, re.I):
            return None
        reason = (f"{role}; description contains accounting/finance responsibility evidence"
                  if description.strip() else f"{role}; responsibilities missing, confirm accounting/finance scope")
        return role, "REVIEW NEEDED", reason
    if role in {name for name, _ in ADJACENT_ROLES}:
        return role, "REVIEW NEEDED", f"Adjacent senior/management role family: {role}"
    return role, "CLEAR MATCH", f"Primary role family: {role}"


def load_commute_preferences(path=ROOT / "search_rules.md"):
    text = path.read_text(encoding="utf-8-sig")
    section = text.split("## Commute Preferences", 1)[1]
    settings = json.loads(re.search(r"```json\s*(.*?)\s*```", section, re.S).group(1))
    if settings["commute_mode"] not in {"driving", "transit"}:
        raise ValueError("Unsupported commute mode")
    if not settings["commute_origin"].strip() or settings["commute_max_minutes"] <= 0:
        raise ValueError("Invalid commute preferences")
    return settings


def load_commute_reviews(path=ROOT / "commute_reviews.json"):
    if not path.exists():
        return {}
    reviews = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(reviews, dict):
        raise ValueError("Commute reviews must be an object keyed by source job ID")
    return reviews


def assess_commute(job, settings, reviews, today=None):
    """Only recorded, current, two-direction route checks can establish fit."""
    today = today or datetime.now(timezone.utc).date()
    origin = settings["commute_origin"]
    review = reviews.get(job["id"], {})
    destination = f"{job['company']}, {job['location']}"
    bucket = "Commute unverified"
    note = "Confirm the actual office and check both directions at your expected work times."
    valid = False
    if isinstance(review, dict) and review:
        try:
            age = (today - datetime.strptime(review["checked_on"], "%Y-%m-%d").date()).days
            durations = [review["outbound_minutes"], review["return_minutes"]]
            valid = (0 <= age <= 30 and review["origin"] == origin
                     and review["mode"] == settings["commute_mode"]
                     and review["listing_location"] == job["location"]
                     and bool(review["office_address"].strip())
                     and bool(review["arrival_time"].strip()) and bool(review["leave_work_time"].strip())
                     and all(type(n) in (int, float) and 0 < n < float("inf") for n in durations))
        except (KeyError, TypeError, ValueError, AttributeError):
            valid = False
        if valid:
            destination = review["office_address"]
            fits = max(durations) <= settings["commute_max_minutes"]
            bucket = "Practical now — route checked" if fits else "Stretch — over commute target"
            note = (f"Recorded estimates: {durations[0]} minutes outbound, {durations[1]} minutes return; "
                    f"checked {review['checked_on']} for arrival {review['arrival_time']} and departure "
                    f"{review['leave_work_time']}. Estimates are not guarantees.")
        else:
            note = "Saved route check is incomplete, over 30 days old, or no longer matches this commute. Recheck both directions."
    if not valid and re.search(r"\bremote\b", job["location"], re.I):
        bucket = "Remote — eligibility unverified"
        note += " Confirm California eligibility and any required office attendance."
    def route(start, end):
        return "https://www.google.com/maps/dir/?" + urlencode({
            "api": 1, "origin": start, "destination": end, "travelmode": settings["commute_mode"]})
    return {"bucket": bucket, "note": note, "outbound_url": route(origin, destination),
            "return_url": route(destination, origin), "destination_confirmed": valid}


def select_discovery(jobs, settings, reviews):
    """Include every passed-in job; use canonical employer grouping and stable order."""
    for job in jobs:
        job["commute"] = assess_commute(job, settings, reviews)
    return sorted(jobs, key=lambda j: (
        j["company"].casefold(), j.get("employer_id", j["company"]),
        j["review_status"] != "CLEAR MATCH", PRIORITY[j["role"]],
        j["title"].casefold(), j["id"]))


def classify_location(location):
    """Conservative location-label policy: unknown places stay visible for review."""
    remote = bool(re.search(r"\bremote\b", location, re.I))
    ca = bool(re.search(r"\bCalifornia\b|\bCA\b", location, re.I))
    if remote and re.search(
            r"\b(?:except|excluding|not(?: available| eligible)?(?: in| for)?|ineligible in)\s+(?:residents of )?(?:CA|California)\b"
            r"|\b(?:CA|California)\s+(?:excluded|not eligible|ineligible)\b",
            location, re.I):
        return "INCOMPATIBLE", "Location explicitly excludes California"
    # Explicit non-CA state labels or named foreign restrictions are evidence;
    # unrecognized city names alone are not a reason to discard a role.
    other_states = ("AL|AK|AZ|AR|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|"
                    "MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY|DC")
    restricted = re.search(r",\s*(?:" + other_states + r")\b", location)
    if remote:
        restricted = restricted or re.search(r"\b(?:" + other_states + r")\b", location)
    restricted = restricted or re.search(
        r"\b(?:Texas|New York|Florida|United Kingdom|UK|Canada|Germany|India|Australia)\b", location, re.I)
    if remote and ca and restricted:
        return "REVIEW NEEDED", "REVIEW NEEDED — LOCATION: mixed region labels; confirm California eligibility"
    if remote and ca and re.search(r"\b(?:not|except|excluding|ineligible)\b", location, re.I):
        return "REVIEW NEEDED", "REVIEW NEEDED — LOCATION: remote restriction needs review"
    if remote and re.search(r"\b(?:all 50 states|anywhere in (?:the )?(?:US|USA|United States))\b", location, re.I):
        return "COMPATIBLE", "Nationwide remote eligibility explicitly listed; verify attendance"
    if restricted and not ca:
        return "INCOMPATIBLE", "Location lists an outside-area state/region; excluded from normal discovery"
    if re.search(r"\b(Los Angeles|Hawthorne|Long Beach|El Segundo|Santa Monica|Pasadena|Culver City|Torrance|Burbank|Glendale)\b",
                 location, re.I):
        return "COMPATIBLE", "LA-area listed; verify office attendance and commute"
    if remote and ca:
        return "COMPATIBLE", "Remote California listed; verify employer eligibility and attendance"
    return "REVIEW NEEDED", "REVIEW NEEDED — LOCATION: confirm LA-area access or California remote eligibility"


def location_status(location):
    return classify_location(location)[1]


def salary_evidence(description):
    excerpts = []
    covered_until = -1
    for match in re.finditer(r"\$\s*\d[\d,]*(?:\.\d+)?\s*[kK]?", description):
        if match.start() < covered_until:
            continue
        snippet = description[max(0, match.start()-90):min(len(description), match.end()+160)].strip()
        excerpts.append(snippet)
        covered_until = match.end()+160
    return excerpts[:4]


def evaluate(job, weights, rejects):
    classification = classify_role(job["title"], job["description"], rejects)
    if classification is None:
        return None
    role, review_status, reason = classification
    evidence = []
    for signal, points in weights.items():
        match = re.search(PATTERNS[signal], job["description"], re.I)
        if match:
            evidence.append({"signal": signal, "points": points,
                             "excerpt": job["description"][max(0, match.start()-45):match.end()+90]})
    warnings = [f"Excluded-topic mention: {term}; review role focus" for term in rejects
                if term in job["description"].lower()]
    if not job["description"]:
        warnings.append("Description missing; title classification is not verified suitability")
    geography, location_review = classify_location(job["location"])
    if geography != "COMPATIBLE":
        warnings.append(location_review)
    if warnings:
        review_status = "REVIEW NEEDED"
    return {**job, "role": role, "classification_reason": reason,
            "accounting_signal_coverage": round(100*sum(e["points"] for e in evidence)/sum(weights.values())),
            "evidence": evidence, "location_classification": geography, "location_review": location_review,
            "salary_excerpts": salary_evidence(job["description"]), "warnings": warnings,
            "review_status": review_status}


def md(value):
    # All external text is rendered as one escaped inline value, including headings.
    value = " ".join(str(value).split())
    value = html.escape(value, quote=False).replace("\\", "\\\\")
    for char in chr(96) + "*_{}[]()#+.!|~-":
        value = value.replace(char, "\\" + char)
    return value


def render_report(run):
    sources = run["sources"]
    selected_count = len(sources)
    active_count = run.get("active_source_count", selected_count)
    failed = any(not source["ok"] for source in sources)
    subset = selected_count < active_count
    if failed or subset or not sources:
        coverage = "INCOMPLETE — failed or unsearched ACTIVE sources; missing opportunities are unknown."
    else:
        coverage = "All selected ACTIVE sources fetched successfully; recognized opportunities are untruncated."
    lines = ["# Job Scout Discovery", "", f"Retrieved: {md(run['retrieved_at'])}", "",
             f"Source coverage: {coverage}",
             "All recognized eligible jobs from successful selected sources are shown under the documented title/location rules.",
             "This does not guarantee that every relevant job was recognized; failed sources leave unknown gaps.",
             "CLEAR MATCH means a primary role-family title, not candidate fit. REVIEW NEEDED requires inspection.",
             "Accounting-signal coverage measures weighted vocabulary evidence, not hiring probability, suitability or job quality.",
             "Salary and accounting-signal coverage do not control inclusion or ordering.", "",
             f"Fetched {run['fetched_count']} postings; recognized {run['target_count']} accounting/finance roles; displaying {len(run['jobs'])}.",
             f"Outside-area roles omitted from this view: {run.get('excluded_location_count', 0)}; retained in history. Use --all-locations to inspect them.",
             "Discovery includes handled states. Only NEW/SHORTLISTED are unhandled by job state; this is not an application recommendation.",
             f"Unhandled displayed jobs within the broad location policy: {len(run.get('fresh_job_ids', []))}.",
             "Employer controls apply to the separate selection view; complete discovery remains visible.",
             "", "## Application selection", "",
             "Eligible for human consideration under current job/location/employer controls; not a submitted application or verified fit.",
             f"Jobs available for consideration: {len(run.get('selection_job_ids', []))}.",
             *[f"- {md(job_id)}" for job_id in run.get("selection_job_ids", [])],
             "", "## Source health", ""]
    if "active_employer_count" in run:
        lines.append(f"Configured ACTIVE employers: {run['active_employer_count']} (Product Owner-configured search cycle; no fixed count quota. PILOT is not APPROVED).")
    lines.append(f"Selected source boards: {selected_count} of {active_count} ACTIVE boards.")
    for source in sources:
        lines.append(f"- {md(source['board'])}: {md(source['status'])}")
    # Production groups come from the canonical registry, including zero-yield employers.
    employers = run.get("employers")
    if employers is None:
        employers = list({j.get("employer_id", j["company"]): {
            "employer_id": j.get("employer_id", j["company"]), "company": j["company"]}
            for j in run["jobs"]}.values())
    for employer in employers:
        employer_id = employer["employer_id"]
        jobs = [j for j in run["jobs"] if j.get("employer_id", j["company"]) == employer_id]
        lines += ["", f"## {md(employer['company'])}", "",
                  f"Employer ID: {md(employer_id)}"]
        if "approval_status" in employer:
            lines.append(f"Registry status: {md(employer['approval_status'])}")
        relationship = employer.get("relationship")
        if relationship:
            lines += [f"**{md(relationship['status'])}**", md(relationship["reason"])]
            if any(r["kind"] == "ACTIVE APPLICATION" for r in relationship["restrictions"]):
                lines.append("**ACTIVE APPLICATION AT THIS EMPLOYER — REVIEW BEFORE SECOND APPLICATION**")
        if not jobs:
            lines += ["", "No displayed roles from this employer's successful sources under this view's rules; check source health for missing data."]
        for job in jobs:
            commute = job.get("commute")
            # Preserve validated, encoded autolinks: source URLs are not Markdown syntax.
            application_url = html.escape(quote(validate_application_url(job["url"]),
                                               safe=":/?#[]@!$&'()*+,;=%-._~"), quote=False)
            status = job.get("application_status", "NEW")
            state_note = ("Unhandled by job state — inspect role and location before applying."
                          if status in FRESH_STATES else "Handled state — not a fresh application recommendation.")
            lines += ["", f"### {md(job['title'])}", "",
                      f"**{md(job['review_status'])}** — {md(job['classification_reason'])}", "",
                      f"Job ID: {md(job['id'])} · Job state: {md(status)}",
                      state_note,
                      md(job.get("selection_reason", "Inspect current employer relationship before application selection.")),
                      f"Location: {md(job['location'] or 'Not listed')}. {md(job['location_review'])}.", "",
                      f"Application: <{application_url}>", "",
                      f"Accounting-signal coverage: {job['accounting_signal_coverage']}/100 (informational).",
                      "", "**Accounting evidence**"]
            lines += [f"- {md(e['signal'])} (+{e['points']} raw points): {md(e['excerpt'])}"
                      for e in job["evidence"]] or ["- No configured accounting signals found; title remains visible."]
            lines += ["", "**Pay evidence — employer excerpts; confirm base pay, currency and period**"]
            lines += [f"- {md(s)}" for s in job["salary_excerpts"]] or ["- No dollar-denominated pay found; salary is unknown."]
            lines += ["", "**Review flags**"]
            lines += [f"- {md(w)}" for w in job["warnings"]] or ["- Confirm the listing, requirements and office attendance with the employer."]
            if commute:
                lines += ["", f"Optional commute check: [Morning route]({commute['outbound_url']}) · [Return route]({commute['return_url']}). Confirm the office destination."]
                lines.append(md(commute["note"]))
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boards", nargs="+", help="ACTIVE Greenhouse board tokens explicitly mapped in the registry")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--all-locations", action="store_true")
    parser.add_argument("--limit", nargs="?", const="retired", help="Retired: discovery is untruncated")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    parser.add_argument("--state-file", type=Path, default=DEFAULT_PATH,
                        help="Persistent local SQLite database; independent of report output")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--mark", nargs=2, metavar=("JOB_ID", "STATE"),
                         help=f"Job label only, NOT an application record: {', '.join(STATES)}. Lifecycle labels require reconciliation.")
    actions.add_argument("--record-application", metavar="JOB_ID", help="Record an actual submitted application; never submits one")
    actions.add_argument("--application-event", nargs=2, metavar=("APPLICATION_ID", "EVENT"))
    actions.add_argument("--applications", action="store_true", help="Inspect explicit application and decision history as JSON")
    actions.add_argument("--employer-status", metavar="EMPLOYER_ID")
    actions.add_argument("--authorize-opportunity", nargs=2, metavar=("EMPLOYER_ID", "JOB_ID"))
    actions.add_argument("--resolve-reapply-review", metavar="EMPLOYER_ID")
    actions.add_argument("--reconcile-legacy", nargs=2, metavar=("EMPLOYER_ID", "JOB_ID"))
    parser.add_argument("--reason", help="Required human reason for closure, override or reconciliation; stored privately")
    parser.add_argument("--occurred-at", help="Known date or timezone-aware ISO timestamp; omitted means UNKNOWN")
    parser.add_argument("--engagement", choices=("UNKNOWN", "NO", "YES"), default=None)
    parser.add_argument("--disposition", choices=("ELIGIBLE", "REVIEW", "LINKED"))
    parser.add_argument("--application-id", type=int, help="Existing explicit application for LINKED reconciliation")
    actions.add_argument("--history", action="store_true", help="Print saved records as JSON without fetching feeds")
    actions.add_argument("--migrate-state", action="store_true",
                         help="Explicit schema migration only; requires approved private backup/restoration plan")
    args = parser.parse_args(argv)
    if args.limit is not None:
        parser.error("--limit is retired. Remove it: discovery now includes all eligible opportunities.")
    if args.reason is not None and not (args.application_event or args.authorize_opportunity or args.resolve_reapply_review or args.reconcile_legacy):
        parser.error("--reason requires an event or explicit employer decision")
    if args.occurred_at is not None and not (args.record_application or args.application_event):
        parser.error("--occurred-at requires an application or event")
    if args.engagement is not None and not args.application_event:
        parser.error("--engagement requires --application-event")
    if (args.disposition is not None or args.application_id is not None) and not args.reconcile_legacy:
        parser.error("Reconciliation options require --reconcile-legacy")
    try:
        result = None
        if args.record_application:
            result = {"application_id": record_application(args.state_file, args.record_application, args.occurred_at),
                      "message": "Recorded your application fact locally; no application submitted by Scout."}
        elif args.application_event:
            app_id, event = args.application_event
            record_event(args.state_file, int(app_id), event, args.engagement or "UNKNOWN", args.occurred_at, args.reason)
            result = {"application_id": int(app_id), "event": event, "message": "Event appended; prior history retained."}
        elif args.applications:
            result = read_applications(args.state_file)
        elif args.employer_status:
            result = employer_relationships(args.state_file).get(args.employer_status)
            if result is None:
                raise ValueError("Unknown canonical employer ID")
        elif args.authorize_opportunity:
            employer_id, job_id = args.authorize_opportunity
            result = {"decision_id": decide(args.state_file, employer_id, "OVERRIDE", args.reason, job_id),
                      "employer_id": employer_id, "job_id": job_id,
                      "message": "Authorized consideration of this opportunity under the recorded restriction context only; no application submitted."}
        elif args.resolve_reapply_review:
            result = {"decision_id": decide(args.state_file, args.resolve_reapply_review, "REVIEW_CLEARED", args.reason),
                      "message": "Current reapply review resolved; other active/legacy restrictions remain effective."}
        elif args.reconcile_legacy:
            if args.disposition is None:
                raise ValueError("Legacy reconciliation requires --disposition ELIGIBLE, REVIEW or LINKED")
            employer_id, job_id = args.reconcile_legacy
            result = {"decision_id": decide(args.state_file, employer_id, "LEGACY_" + args.disposition,
                                           args.reason, job_id, args.application_id),
                      "message": "Explicit current relationship decision recorded; legacy facts/history unchanged."}
        if result is not None:
            print(json.dumps(result, indent=2, ensure_ascii=True))
            return 0
        if args.migrate_state:
            migrate_database(args.state_file, load_registry(args.registry))
            print("Application-state schema is version 3; legacy labels preserved, no application history inferred; no feeds fetched.")
            return 0
        if args.mark:
            mark_job(args.state_file, *args.mark)
            print(json.dumps({"job_id": args.mark[0], "state": args.mark[1],
                              "message": "Job label only; no application recorded. Legacy application labels require explicit reconciliation."}))
            return 0
        if args.history:
            # ASCII escapes keep JSON portable through Windows console encodings.
            print(json.dumps(read_history(args.state_file), indent=2, ensure_ascii=True))
            return 0
        registry = load_registry(args.registry)
        selected_sources = select_sources(registry, args.boards)
        if not selected_sources:
            raise ValueError("No ACTIVE sources configured; no feeds fetched")
        record_jobs(args.state_file, [], registry)  # Validate state before any feeds.
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Application state unavailable; stopped without a discovery report ({error})", file=sys.stderr)
        return 3
    weights, rejects = load_rules()
    commute_preferences = load_commute_preferences()
    try:
        commute_reviews = load_commute_reviews()
    except (OSError, ValueError) as error:
        print(f"Optional commute notes unavailable; continuing job search ({error})", file=sys.stderr)
        commute_reviews = {}
    sources, candidates, seen, observations = [], [], set(), []
    fetched = 0
    for board, employer in selected_sources.items():
        observed_at = datetime.now(timezone.utc).isoformat()
        try:
            jobs = fetch_jobs(board, employer["display_name"])
            if any(not isinstance(job.get("id"), str) or not job["id"].startswith(board + ":")
                   or not job["id"].split(":", 1)[1] for job in jobs):
                raise ValueError("Source returned an inconsistent job identity")
        except (URLError, TimeoutError, OSError, ValueError, KeyError) as error:
            sources.append({"board": board, "status": f"FAILED: {error}", "ok": False})
            observations.append({"board": board, "observed_at": observed_at, "success": False,
                                 "fetched_count": None, "relevant_count": None,
                                 "error_kind": type(error).__name__})
            print(f"{board}: failed ({error})", file=sys.stderr)
            continue
        sources.append({"board": board, "status": f"OK — {len(jobs)} postings", "ok": True})
        fetched += len(jobs)
        relevant_count = 0
        for job in jobs:
            if job["id"] in seen:
                continue
            seen.add(job["id"])
            result = evaluate(job, weights, rejects)
            if result:
                result["employer_id"] = employer["employer_id"]
                result["company"] = employer["display_name"]
                candidates.append(result)
                relevant_count += 1
        sources[-1]["status"] += f"; {relevant_count} recognized accounting/finance roles"
        observations.append({"board": board, "observed_at": observed_at, "success": True,
                             "fetched_count": len(jobs), "relevant_count": relevant_count,
                             "error_kind": None})
    try:
        statuses = record_jobs(args.state_file, candidates, registry, observations)
        relationships = employer_relationships(args.state_file)
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Application state unavailable; stopped without a discovery report ({error})", file=sys.stderr)
        return 3
    for job in candidates:
        job["application_status"] = statuses[job["id"]]
        allowed, reason = consideration(relationships[job["employer_id"]], job["id"])
        job["selection_eligible"] = (allowed and statuses[job["id"]] in FRESH_STATES
                                     and job["location_classification"] != "INCOMPATIBLE")
        job["selection_reason"] = reason
        if statuses[job["id"]] not in FRESH_STATES:
            job["selection_reason"] += "; handled job state excludes this job from fresh selection"
        if job["location_classification"] == "INCOMPATIBLE":
            job["selection_reason"] += "; incompatible location excludes this job from fresh selection"
    eligible = [j for j in candidates
                if args.all_locations or j["location_classification"] != "INCOMPATIBLE"]
    selected = select_discovery(eligible, commute_preferences, commute_reviews)
    fresh_ids = [j["id"] for j in selected if j["application_status"] in FRESH_STATES
                 and j["location_classification"] != "INCOMPATIBLE"]
    employers = {e["employer_id"]: {"employer_id": e["employer_id"], "company": e["display_name"],
                                   "approval_status": e["approval_status"],
                                   "relationship": {k: relationships[e["employer_id"]][k]
                                                    for k in ("status", "reason", "restrictions", "overrides")}}
                 for e in selected_sources.values()}
    active_sources = select_sources(registry)
    now = datetime.now(timezone.utc)
    run = {"retrieved_at": now.isoformat(), "fetched_count": fetched, "target_count": len(candidates),
           "sources": sources, "jobs": selected, "commute_preferences": commute_preferences,
           "report_type": "complete-discovery", "discovery_policy": "accounting-finance-v3",
           "fresh_job_ids": fresh_ids, "excluded_location_count": len(candidates) - len(selected),
           "selection_job_ids": [j["id"] for j in selected if j["selection_eligible"]],
           "application_policy": "lifecycle-v4",
           "coverage_complete": len(selected_sources) == len(active_sources) and all(s["ok"] for s in sources),
           "employers": sorted(employers.values(), key=lambda e: (e["company"].casefold(), e["employer_id"])),
           "active_source_count": len(active_sources),
           "active_employer_count": sum(e["pool"] == "ACTIVE" for e in registry["employers"])}
    args.output.mkdir(parents=True, exist_ok=True)
    stem = args.output / f"discovery-{now.strftime('%Y%m%d-%H%M%S-%f')}"
    stem.with_suffix(".json").write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    stem.with_suffix(".md").write_text(render_report(run), encoding="utf-8")
    print(f"Fetched {fetched} postings; {len(candidates)} recognized roles; {len(selected)} displayed; {len(fresh_ids)} unhandled by job state and within location policy.")
    for job in run["jobs"]:
        print(f"Accounting-signal coverage {job['accounting_signal_coverage']:3}/100 | {job['company']} | {job['title']} | {job['location']} | {job['review_status']} | {job['id']} | {job['application_status']}")
    print(f"Report: {stem.with_suffix('.md')}")
    if not any(s["ok"] for s in sources):
        return 1
    return 2 if any(not s["ok"] for s in sources) else 0


if __name__ == "__main__":
    raise SystemExit(main())
