# BOOT_CONTEXT.md

# AI Controller Lab — Boot Context

**Current Release:** Job Scout v1.0 (In Progress)

**Last Git Commit:** `41f6ea3`

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

- Replace fragile Indeed-only extraction.
- Connect Job Scout to stable career-page sources.
- Return real accounting jobs with automatic match scoring.

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
- Next refinement: application/new-posting tracking and useful source coverage, guided by daily use.
- Run instructions and limitations are in `job-agent/README.md`; tests in `test_job_scout.py`.
- `job_tracker.csv` remains separate and unchanged. Existing sample rows are not live search results.
- Upgrade decisions live in root `UPGRADE_LEDGER.md`.
- Earlier status sections above describe the starting state; this checkpoint records subsequent progress.

## Close steps

Before ending a build session:

- Verify architecture changes are reflected.
- Reconcile documentation.
- Remove temporary files if needed.
- Run one Git commit.
- Push once to GitHub.
