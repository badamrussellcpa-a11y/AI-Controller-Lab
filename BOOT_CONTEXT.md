# BOOT_CONTEXT.md

## Daily close reconciliation - September 25, 2026

This checkpoint supersedes earlier test-count and security-scan status notes below.
All 34 Job Scout tests pass (22 original, eight persistence, four URL-security
tests). The standard repository security scan completed and reported one
low-severity application-URL/Markdown injection finding. The narrow fix validates
URLs at ingestion and revalidates/encodes them at report output; focused regression
tests pass. This is targeted remediation evidence, not a subsequent full scan.

The recorded isolated live APPLIED acceptance test passed. Full Job Scout v1
acceptance remains open: demonstrate live Controller coverage and review whether
the existing summaries are application-ready. No release tag is declared here.
The daily checkpoint includes application-state persistence, URL hardening, tests,
and the Mentor Mode workpaper. Private databases and generated reports remain
outside Git. Commit/push completion must be verified from Git, not this note.


# AI Controller Lab — Boot Context

**Current Release:** Job Scout v1.0 (In Progress)

**Last Git Commit:** Historical checkpoint `41f6ea3`; use `git log -1` for current HEAD.

**Repository:** AI-Controller-Lab

---

# Session Startup Protocol

Every AI Controller Lab session begins in **Builder Mode**.

Startup phrase:

> **AI Controller Lab. Builder Mode.**

Default assumptions:

- Repository is the source of truth.
- Builder Mode remains active.
- One Git push at Daily Close.
- Full-file replacements instead of piecemeal snippets.
- Interrupt only for meaningful architecture debt, security, data integrity, or irreversible decisions.
- Build workflow: **Architect → Build v1.0 → Test → Fix → Learn afterward.**

---

# Current Mission

Build **Job Scout v1.0** — the first working AI agent that returns real Controller and Senior Accountant jobs from stable career-page sources.

---

# Current Architecture

## Root

- BOOT_CONTEXT.md
- OPERATING_SYSTEM.md
- FOUNDER_PROFILE.md
- PROJECT_CHARTER.md
- ROADMAP.md
- .gitignore
- workpapers/

## Job Agent

- browser.py
- browser_test.py
- scraper.py
- job_scout.py
- application_state.py (persistent local SQLite state)
- job_tracker.csv
- master_prompt.md
- search_rules.md

---

# Current Status

## Completed

- Git + GitHub workflow established.
- Python environment configured.
- Playwright installed.
- Browser automation verified.
- Repository cleaned and organized.
- Founder Profile established.
- Workpaper system established.

## In Progress

- Full v1 release acceptance: live Controller coverage and application-ready summaries.
- Separate Codex Security release scan after the verified application-state change.

Live Greenhouse retrieval, transparent scoring, manual Top 5 reports, and persistent
application state are implemented. See the latest checkpoint below and the Job
Scout README for verified behavior and limitations.

---

# Next Mission

Ship **Job Scout v1.0**.

Success means:

- Stable job source connected.
- Real accounting jobs returned.
- Match scores displayed.
- Clean Builder Mode workflow preserved.

---

# Repository Recovery

If starting a new ChatGPT session:

1. Open this file.
2. Paste it into the first message.
3. Continue in **Builder Mode**.

---

# Daily Close Checklist

## Build checkpoint — September 25, 2026

- First live-feed Job Scout pilot implemented in `job-agent/job_scout.py` and `scraper.py`.
- Reads four public employer Greenhouse boards; no paid AI calls or browser needed.
- Writes timestamped shortlist Markdown and JSON in ignored `job-agent/results/`.
- Reads scoring weights from `search_rules.md`; scores are keyword evidence, not hiring probability.
- Live run returned six LA-area accounting candidates. Review usefulness before declaring v1.0 complete.
- Next mission: review live shortlist with Adam, then refine salary/location rules and source coverage.
- Adam reviewed the initial six roles and would consider all; first retrieval functionality accepted as useful.
- Commute preference confirmed: Hollywood Blvd and N Vista St, Los Angeles; driving, 45 minutes each way.
- Latest direction: five relevant jobs per daily review is sufficient. Default shortlist capped at five; runs remain manual.
- Commute is optional context only: no commute quota, commute grouping, or commute-based ranking. Route links remain available.
- No commute times have been verified. Do not spend more build time on commute verification unless Adam requests it.
- At this earlier checkpoint, the next refinement was application tracking; see the completed update below.
- Run instructions and limitations are in `job-agent/README.md`; tests in `test_job_scout.py`.
- `job_tracker.csv` remains separate and unchanged. Existing sample rows are not live search results.
- Upgrade decisions live in root `UPGRADE_LEDGER.md`.
- Earlier status sections above describe the starting state; this checkpoint records subsequent progress.

## Application-state checkpoint — September 25, 2026 (Pacific)

- Added standard-library SQLite storage keyed by source job ID; no new packages or services.
- Manual `--mark ID STATE` and `--history` commands; only NEW/SHORTLISTED qualify for fresh Top 5.
- Handled/absent records survive reruns; all fetched target roles are retained with latest details and timestamps.
- Default database is private and Git-ignored, independent of report output; the sample CSV is untouched.
- 30 automated tests pass, including separate-process acceptance and failure/encoding cases.
- Live acceptance: four feeds succeeded twice; 3,428 postings, nine target roles;
  five recommendations became four after marking one APPLIED in an isolated test store.
  The job was still in the feed, excluded from recommendations, and preserved APPLIED in history.
- Evidence and limitations are documented in `job-agent/README.md`.
- Application-state scope is complete and ready for a separate security scan, not yet security-cleared.
- Full release is not declared complete: roadmap Controller coverage and application-ready
  summary acceptance remain unverified. No source expansion or unrelated features added.
- No push, merge, or release tag performed. Current task requires explicit approval for those actions.

## Close steps

Before ending a build session:

- Verify architecture changes are reflected.
- Reconcile documentation.
- Remove temporary files if needed.
- Run one Git commit.
- Push once to GitHub.
