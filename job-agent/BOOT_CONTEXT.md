
# AI Controller Lab — Boot Context

Purpose: Reload the project before building.

This file is the AI boot sequence. It is operational documentation, not a study guide.

---

## Operating Mode

- Default mode: Build Mode
- Deliver complete working files (Safe Copy)
- Include a File Manifest before coding
- Keep explanations short during builds
- Save deeper explanations for the Workpaper
- End every session with Daily Close

---

## Current Project State

Release: Pre-v1.0

Latest Git Commit: 33fb28b

Repository Status:
- GitHub synced
- Working tree clean

---

## Current Mission

Complete Job Scout v1.0.

Definition of Done:

`python job_scout.py`

returns real Controller and Senior Accountant job listings from a stable career source.

---

## Active Architecture

Repository:

AI-Controller-Lab/

Key project files:

- PROJECT_CHARTER.md
- ROADMAP.md
- OPERATING_SYSTEM.md *(to be created)*
- BOOT_CONTEXT.md
- workpapers/
- job-agent/browser.py
- job-agent/scraper.py
- job-agent/job_scout.py
- job-agent/job_tracker.csv

Current known status:

- Git workflow works.
- Python 3.14.7 installed.
- Playwright installed.
- Chromium installed.
- Browser automation works.
- Indeed selectors proved unreliable.
- Architecture is separated into browser, scraper, and orchestrator.

---

## Project Principles

- Build first.
- Learn second.
- Preserve always.
- Time-box investigations.
- Optimize for recoverable assets.
- Learn one abstraction above what AI automates.

---

## Build Session Format

Every feature follows this order:

1. Mission
2. One X-Ray concept
3. Safe Copy
4. Run
5. Git commit

Long explanations belong in the Workpaper.

---

## Daily Close Requirements

Before ending a session:

1. Run final tests.
2. `git status`
3. `git add .`
4. `git commit`
5. `git push`
6. Update BOOT_CONTEXT.md.
7. Create today's Workpaper.
8. Record Recovery Checkpoint.

---

## Recovery Checkpoint

Current commit: 33fb28b

Next objective:

Build Job Scout v1.0 using a stable career-page source instead of relying solely on Indeed.
