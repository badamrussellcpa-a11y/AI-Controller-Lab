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
- **Post-checkpoint evidence:** Adam reports a live run of 915 postings → 20
  recognized roles → 18 displayed/unhandled under normal location policy. Independent
  AI-assisted research found substantially the same useful roles within these seven
  employers. See the operating guide for provenance and limits. Configured Greenhouse
  coverage excludes employers on other systems; this is not market completeness.
- **Still open:** Does repeatability/state/scale/control justify maintenance over
  reasoning-AI-assisted discovery? Review minimal Job Scout closure/release disposition
  before shifting focus. No commercial validation or v1 release is claimed. Optional
  Excel/portfolio/multi-ATS work is unapproved; any private migration and final release
  security review remain separately controlled. Future cohorts need new approval.
- **Next major direction:** AI Controller Capability Benchmark planning, comparing
  reasoning AI, existing accounting/office tools and a manual baseline before building
  demonstrated gaps. Older bank-reconciliation/Controller Copilot ideas are candidates,
  not automatic implementation instructions. Lumina Wearables and Life Admin remain
  future/learning ideas; no sensitive-data access is authorized.

The project clarified a distinction that was insufficiently explicit at inception:
Atlas/reasoning AI → Codex/implementation agent → deterministic Python/SQLite Scout.
An intelligent builder does not automatically give its software contextual reasoning.
Future substantial builds use the integrated **Build-vs-Existing Capability Gate** in
[OPERATING_SYSTEM.md](OPERATING_SYSTEM.md); [WP-012](workpapers/WP-012.md) explains
this learning through the actual acceptance example.

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
