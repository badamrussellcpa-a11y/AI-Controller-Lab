# AI Controller Lab

A hands-on software engineering and automation lab led by Adam Russell, CPA.

## Start or recover a session

> AI Controller Lab. Continue from repository state.

Read [OPERATING_SYSTEM.md](OPERATING_SYSTEM.md) → [SECURITY.md](SECURITY.md) →
[BOOT_CONTEXT.md](BOOT_CONTEXT.md) → [ROADMAP.md](ROADMAP.md) and the
[Job Scout product contract](job-agent/master_prompt.md), then inspect current
Git state read-only. Repository evidence takes precedence over conversational memory.

## Built versus planned

- **Job Scout: working local system; v1 in progress.** Public Greenhouse retrieval,
  broad deterministic role/location classification, complete employer-grouped
  discovery reports with informational accounting-signal coverage,
  private SQLite job state, employer registry/canonical identity, explicit pool
  placement, schema versioning and source-run observations are implemented. Task 4
  adds explicit application/event history, derived employer selection controls,
  reapply review, job-specific overrides and legacy reconciliation. Task 5 configures
  seven Product Owner-approved ACTIVE employers for the current search cycle:
  Muck Rack, LaunchDarkly, BaubleBar, Airtable, Figma, Reddit and Rocket Lab.
  SpaceX is retained PAUSED. Seven is intentional; ACTIVE is not a quota. See the
  [current operating guide](job-agent/README.md).
- **Still open:** Product Owner usefulness comparison with separate ChatGPT/manual
  research, optional minimal portfolio/Excel work, any separately authorized private
  migration, final security review and Release Close. Employer selection belongs to
  human + AI judgment; Scout executes approved configuration without an employer
  scoring algorithm. Future cohorts require separate Product Owner approval.
- **Future/learning projects:** Lumina Wearables training company, Controller
  Copilot (bank reconciliation, month-end close, audit PBC assistance), and Life
  Admin. These entries do not claim implemented production systems or authorize
  access to accounting/personal data.

## Document ownership

OPERATING_SYSTEM owns permanent Daily Close, Release Close, recovery and working
procedures. BOOT_CONTEXT owns current status and the exact next task; ROADMAP owns
milestones and release gates. Job Scout's README describes actual operation;
master_prompt owns the approved product contract; search_rules holds current
runtime settings and clearly marked future policy. SECURITY governs security;
UPGRADE_LEDGER records actual cost decisions. Dated workpapers preserve history
and learning, not competing current instructions.

No v1 release is declared. Older Top-5 and runtime application-writing acceptance
requirements are superseded by the approved redesign, not retroactively passed.
