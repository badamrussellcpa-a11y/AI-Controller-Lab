
# AI Controller Lab Operating System v1.0

This document is the project's source of truth for how development happens.

---

# Build Mode (Default)

Every feature follows this sequence.

1. Mission
2. One X-Ray concept
3. File Manifest
4. Safe Copy (complete working files)
5. Run command
6. Git commit

The goal is momentum.

Do not interrupt builds with long tutorials.

Long explanations belong in the Workpaper.

---

# Safe Copy Rule

Unless we're intentionally learning Git differences, provide complete working files.

Never require hunting for individual lines.

---

# File Manifest Rule

Every build begins by listing exactly which files will change.

Example:

- job-agent/scraper.py
- job-agent/job_scout.py

---

# Daily Close (Required)

Every session ends with four deliverables.

1. Final tests
2. Git commit and push
3. Updated BOOT_CONTEXT.md
4. New Workpaper

Nothing important stays trapped in chat.

---

# Recovery Checkpoint

Every close records:

- Release
- Git Commit
- GitHub Status
- Working Tree Status
- Next Mission

This becomes the project's restart point.

---

# Time-Box Rule

Investigate bugs for a reasonable amount of time.

If a third-party website becomes fragile, pivot instead of spending hours chasing selectors.

---

# Project Principles

- Build first.
- Learn second.
- Preserve always.
- Optimize for recoverable assets.
- Learn one abstraction above what AI automates.

---

# Institutional Memory

The project has three layers of memory.

- Chat = working memory
- GitHub = permanent memory
- BOOT_CONTEXT.md = behavioral reboot

Every new build session should reload BOOT_CONTEXT before continuing.
