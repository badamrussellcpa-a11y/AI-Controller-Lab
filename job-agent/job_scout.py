
"""Fetch and rank accounting jobs with transparent evidence, without paid AI calls."""
import argparse
from datetime import datetime, timezone
import json
import html
from pathlib import Path
import re
import sys
import sqlite3
from application_state import DEFAULT_PATH, FRESH_STATES, STATES, mark_job, read_history, record_jobs
from urllib.error import URLError
from urllib.parse import quote, urlencode
from scraper import fetch_jobs, validate_application_url

ROOT = Path(__file__).resolve().parent
BOARDS = {"rocketlab": "Rocket Lab", "spacex": "SpaceX", "figma": "Figma", "reddit": "Reddit"}
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
ROLES = [
    ("Assistant Controller", r"\bassistant controller\b"),
    ("Controller", r"\bcontroller\b"),
    ("Accounting Manager", r"\baccounting manager\b|\bmanager[, -]+(?:technical |corporate )?accounting\b"),
    ("Senior Accountant", r"\b(?:senior|sr\.?) accountant\b"),
    ("Finance Manager", r"\bfinance manager\b"),
]
PRIORITY = {"Controller": 0, "Assistant Controller": 1, "Accounting Manager": 2,
            "Senior Accountant": 3, "Finance Manager": 4}


def load_rules(path=ROOT / "search_rules.md"):
    text = path.read_text(encoding="utf-8-sig")
    weights = {name.strip(): int(points) for name, points in
               re.findall(r"\|\s*([^|\n]+?)\s*\|\s*\+(\d+)\s*\|", text)}
    if set(weights) != set(PATTERNS) or sum(weights.values()) == 0:
        raise ValueError("Scoring table differs from supported signals; update patterns alongside rules")
    section = text.split("## Automatic Reject", 1)[1].split("\n## ", 1)[0]
    return weights, [word.strip().lower() for word in re.findall(r"^- (.+)$", section, re.MULTILINE)]


def role_for(title):
    if re.search(r"\b(hardware|software|engineer|document|flight|traffic|inventory)\b", title, re.I):
        return None
    for role, pattern in ROLES:
        if re.search(pattern, title, re.I):
            return role
    return None


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


def select_shortlist(jobs, settings, reviews, limit):
    for job in jobs:
        job["commute"] = assess_commute(job, settings, reviews)
    jobs.sort(key=lambda j: (bool(j["warnings"]), -j["score"],
                             PRIORITY[j["role"]], j["company"], j["id"]))
    return jobs[:limit]


def location_status(location):
    if re.search(r"\b(Los Angeles|Hawthorne|Long Beach|El Segundo|Santa Monica|Pasadena|Culver City|Torrance|Burbank|Glendale)\b", location, re.I):
        return "LA-area; verify commute and attendance"
    if re.search(r"\bremote\b", location, re.I):
        return "Remote listed; verify California eligibility"
    return "Location outside known LA locations or unclear"


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
    role = role_for(job["title"])
    if not role or any(term in job["title"].lower() for term in rejects):
        return None
    evidence = []
    for signal, points in weights.items():
        match = re.search(PATTERNS[signal], job["description"], re.I)
        if match:
            evidence.append({"signal": signal, "points": points,
                             "excerpt": job["description"][max(0, match.start()-45):match.end()+90]})
    if role == "Finance Manager":
        signals = {item["signal"] for item in evidence}
        if "Team leadership" not in signals or not signals.intersection({"Month-end close", "General ledger ownership", "Financial reporting"}):
            return None
    warnings = [f"Excluded-topic mention: {term}; review role focus" for term in rejects
                if term in job["description"].lower()]
    if not job["description"]:
        warnings.append("Description missing; score cannot establish suitability")
    return {**job, "role": role, "score": round(100*sum(e["points"] for e in evidence)/sum(weights.values())),
            "evidence": evidence, "location_review": location_status(job["location"]),
            "salary_excerpts": salary_evidence(job["description"]), "warnings": warnings,
            "review_status": "REVIEW" if warnings else "Candidate"}


def md(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("[", "\\[").replace("]", "\\]").replace("*", "\\*").replace("_", "\\_").replace("`", "\\`")


def render_report(run):
    lines = ["# Job Scout — live shortlist", "", f"Retrieved: {run['retrieved_at']}", "",
             "Scores measure keyword evidence, not hiring probability or verified qualifications.",
             "Location eligibility, base salary and role suitability require your review.", "",
             f"This run searches {len(run['sources'])} selected employer feeds, not the whole job market. Salary does not affect the score.",
             "Your preference: $120,000+ ideal; consider strong opportunities from $100,000. Compare the pay evidence below.", "",
             f"Fetched {run['fetched_count']} postings; found {run['target_count']} target-role candidates; showing {len(run['jobs'])}.",
             ""]
    lines += ["Ranked by accounting evidence and role priority; commute checks do not change ranking or eligibility.",
              "Default: up to five jobs to review. Only NEW and SHORTLISTED jobs are eligible; previously seen unhandled jobs can reappear.", ""]
    lines += ["", "## Source health", ""]
    for source in run["sources"]:
        lines.append(f"- {md(source['board'])}: {md(source['status'])}")
    if not run["jobs"]:
        lines += ["", "No candidates passed this run's filters. This does not mean no matching jobs exist elsewhere."]
    for index, job in enumerate(run["jobs"], 1):
        commute = job.get("commute")
        # An autolink isolates URL punctuation from Markdown; encode delimiters
        # and escape entities without decoding or rewriting stored source URLs.
        application_url = html.escape(quote(validate_application_url(job["url"]),
                                           safe=":/?#[]@!$&'()*+,;=%-._~"), quote=False)
        lines += ["", f"## {index}. {md(job['title'])} — {md(job['company'])}", "",
                  f"**Evidence score: {job['score']}/100 · {job['review_status']}**", "",
                  f"Job ID: {md(job['id'])} · Application state: {md(job.get('application_status', 'NEW'))}", "",
                  f"Location: {md(job['location'] or 'Not listed')}. {md(job['location_review'])}.", "",
                  f"Application: <{application_url}>"]
        lines += ["", "**Why it surfaced**"]
        lines += [f"- {md(e['signal'])} (+{e['points']} raw points): {md(e['excerpt'])}" for e in job["evidence"]] or ["- No scoring signals found."]
        lines += ["", "**Pay evidence — employer excerpts; confirm base pay, currency and period**"]
        lines += [f"- {md(s)}" for s in job["salary_excerpts"]] or ["- No dollar-denominated pay found; salary is unknown."]
        lines += ["", "**Before applying**", "- Confirm the job is still open and you meet location and experience requirements."]
        lines += [f"- {md(w)}" for w in job["warnings"]]
        if job["evidence"]:
            lines += [f"- Resume focus, if supported by your experience: {md(', '.join(e['signal'] for e in job['evidence'][:3]))}. Add your own truthful accomplishments."]
        if commute:
            lines += ["", f"Optional commute check: [Morning route]({commute['outbound_url']}) · [Return route]({commute['return_url']}). Confirm the office destination."]
            if commute["destination_confirmed"]:
                lines += [md(commute["note"])]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boards", nargs="+", default=list(BOARDS), help="Greenhouse board tokens")
    parser.add_argument("--all-locations", action="store_true")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    parser.add_argument("--state-file", type=Path, default=DEFAULT_PATH,
                        help="Persistent local SQLite database; independent of report output")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--mark", nargs=2, metavar=("JOB_ID", "STATE"),
                         help=f"Set a known job's state without fetching feeds: {', '.join(STATES)}")
    actions.add_argument("--history", action="store_true", help="Print saved records as JSON without fetching feeds")
    args = parser.parse_args(argv)
    if args.limit < 1:
        parser.error("--limit must be positive")
    try:
        if args.mark:
            mark_job(args.state_file, *args.mark)
            print(f"{args.mark[0]}: {args.mark[1]}")
            return 0
        if args.history:
            # ASCII escapes keep JSON portable through Windows console encodings.
            print(json.dumps(read_history(args.state_file), indent=2, ensure_ascii=True))
            return 0
        record_jobs(args.state_file, [])  # Validate state before fetching any feeds.
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Application state unavailable; stopped without a fresh shortlist ({error})", file=sys.stderr)
        return 3
    weights, rejects = load_rules()
    commute_preferences = load_commute_preferences()
    try:
        commute_reviews = load_commute_reviews()
    except (OSError, ValueError) as error:
        print(f"Optional commute notes unavailable; continuing job search ({error})", file=sys.stderr)
        commute_reviews = {}
    sources, candidates, seen = [], [], set()
    fetched = 0
    for board in dict.fromkeys(args.boards):
        try:
            jobs = fetch_jobs(board, BOARDS.get(board, board))
        except (URLError, TimeoutError, OSError, ValueError, KeyError) as error:
            sources.append({"board": board, "status": f"FAILED: {error}", "ok": False})
            print(f"{board}: failed ({error})", file=sys.stderr)
            continue
        sources.append({"board": board, "status": f"OK — {len(jobs)} postings", "ok": True})
        fetched += len(jobs)
        for job in jobs:
            if job["id"] in seen:
                continue
            seen.add(job["id"])
            result = evaluate(job, weights, rejects)
            if result:
                candidates.append(result)
    try:
        statuses = record_jobs(args.state_file, candidates)
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Application state unavailable; stopped without a fresh shortlist ({error})", file=sys.stderr)
        return 3
    for job in candidates:
        job["application_status"] = statuses[job["id"]]
    eligible = [j for j in candidates if j["application_status"] in FRESH_STATES
                and (args.all_locations or not j["location_review"].startswith("Location outside"))]
    selected = select_shortlist(eligible, commute_preferences, commute_reviews, args.limit)
    now = datetime.now(timezone.utc)
    run = {"retrieved_at": now.isoformat(), "fetched_count": fetched, "target_count": len(candidates),
           "sources": sources, "jobs": selected, "commute_preferences": commute_preferences}
    args.output.mkdir(parents=True, exist_ok=True)
    stem = args.output / f"shortlist-{now.strftime('%Y%m%d-%H%M%S-%f')}"
    stem.with_suffix(".json").write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    stem.with_suffix(".md").write_text(render_report(run), encoding="utf-8")
    print(f"Fetched {fetched} postings; {len(candidates)} target roles; {len(eligible)} eligible by location and application state.")
    for job in run["jobs"]:
        print(f"{job['score']:3}/100 | {job['company']} | {job['title']} | {job['location']} | {job['review_status']} | {job['id']} | {job['application_status']}")
    print(f"Report: {stem.with_suffix('.md')}")
    if not any(s["ok"] for s in sources):
        return 1
    return 2 if any(not s["ok"] for s in sources) else 0


if __name__ == "__main__":
    raise SystemExit(main())
