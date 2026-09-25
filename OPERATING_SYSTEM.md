
# OPERATING_SYSTEM.md

# AI Controller Lab Operating System

This document defines **how we build**, not what we're building.

The goals are simple:

- Ship working software quickly.
- Keep the repository clean.
- Preserve decisions without creating document sprawl.

---

# Builder Mode (Default)

Builder Mode is the default for development sessions.

Every task follows this sequence:

1. Mission
2. X-Ray (one concept only)
3. File Manifest
4. Safe Copy (complete replacement file)
5. Run
6. Verify
7. Git checkpoint

The objective is to maximize momentum while learning through real work.

---

# Safe Copy Rule

Whenever a file changes, provide:

- File changing
- Why it's changing (X-Ray)
- The complete working file

Avoid piecemeal edits unless we're intentionally learning Git or debugging a specific line.

---

# The 80/20 Rule

Momentum beats polish until the deliverable works.

Every suggestion must pass a value gate.

## Priority Ladder

### 🔴 Blocker

Fix immediately.

Examples:

- Import errors
- Broken code
- Failed tests

### 🟠 Important

Bundle into Daily Close.

Examples:

- Repository cleanup
- Documentation updates
- .gitignore improvements

### 🟢 Nice-to-Have

Do not interrupt the build.

Move it to the Parking Lot.

Examples:

- Tiny wording tweaks
- Cosmetic renames
- Extra documentation ideas

---

# Interrupt Budget

During Builder Mode:

- Maximum one unsolicited improvement every 30–60 minutes.
- Otherwise:
  - Fix blockers.
  - Answer the current question.
  - Keep shipping.

This prevents unnecessary context switching.

---

# Daily Close (Mentor Mode)

At the end of every build session:

1. Repository Reconciliation
2. Update BOOT_CONTEXT (if needed)
3. Save today's Workpaper
4. Git status
5. Git add
6. Git commit
7. Git push

Daily Close is the only time we intentionally slow down.

---

# Repository Reconciliation

Before ending a session, verify:

- Architecture changes reflected.
- Documentation reconciled.
- Temporary files cleaned.
- Git committed.
- GitHub synced.

Ask one final question:

> "If someone cloned this repository tomorrow, what would confuse them?"

Fix only meaningful issues.

---

# File Governance

Every file must have one owner and one purpose.

Before creating a new file, perform a Repository Audit.

Ask:

1. Can an existing file absorb this?
2. Does it duplicate another document?
3. Is it temporary?
4. Will Future Adam actually use it?

If the answer doesn't justify a new file, update an existing one instead.

Protected files:

- BOOT_CONTEXT.md
- OPERATING_SYSTEM.md
- PROJECT_CHARTER.md
- ROADMAP.md
- workpapers/
- job-agent/

---

# Operating Principles

- Ship the smallest working deliverable.
- Prefer progress over perfection.
- Preserve recoverable checkpoints.
- Eliminate duplicate documentation.
- Keep the repository lean.

