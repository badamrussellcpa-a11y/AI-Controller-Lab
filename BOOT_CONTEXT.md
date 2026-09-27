# AI Controller Lab — current recovery context

**Updated September 26, 2026. Task 4 implemented; Job Scout v1 remains in progress.**

Permanent procedures: [OPERATING_SYSTEM.md](OPERATING_SYSTEM.md).
Security: [SECURITY.md](SECURITY.md). Product: [job-agent/master_prompt.md](job-agent/master_prompt.md).
Acceptance: [ROADMAP.md](ROADMAP.md). Commands: [job-agent/README.md](job-agent/README.md).

## Current machine

Task 3 complete employer-grouped discovery remains intact: all recognized broadly
location-eligible roles, primary/adjacent classifications, informational coverage,
no Top-5 gate, explicit source-health limits and truthful job states.

Task 4 adds explicit local application records and append-only lifecycle events.
APPLIED, SCREEN, INTERVIEW and unresolved OFFER suppress employer selection.
A closure with explicitly confirmed NO meaningful engagement releases that
application's restriction. Prior YES engagement remains YES; closed processes with
YES or UNKNOWN require REVIEW BEFORE REAPPLYING. A previous NO never proves that
no interaction happened later. Explicit review resolution records reason/time.
Other active applications or unresolved legacy facts still restrict selection.

Complete discovery keeps sibling opportunities visible and warns about employer
restrictions. Sibling job states remain unchanged. selection_job_ids is the normal
controlled selection list; fresh_job_ids remains the Task 3 unhandled-state list,
not the application-selection queue. Report JSON identifies application_policy
lifecycle-v4 separately from discovery_policy accounting-finance-v3.

A reasoned explicit override authorizes one unhandled saved job under the current
restriction context. No timer or company-wide bypass. New applications, closure/
reconciliation/review facts, or changed listing title/location/description/URL need
fresh authorization. Ordinary active-stage progression and unchanged refreshes do
not. Recording an actual application is always a factual local action, never
submission; it must not conceal reality because selection policy discouraged it.

Schema v3 retains the v2 foundation and adds applications, application_events,
legacy_application_facts and employer_decisions. Normal commands refuse v1/v2
migration; explicit transactional migration preserves original records/values.
APPLIED/INTERVIEW/OFFER/REJECTED legacy labels are preserved without inferring
applications, dates or engagement. Unreconciled employers are gated. Explicit
ELIGIBLE/REVIEW/LINKED reconciliation decisions preserve old evidence. --mark is
a discovery-label operation only; it cannot clear legacy restrictions and refuses
jobs backed by explicit applications. --applications inspects full lifecycle and
decision history; --history still inspects job snapshots.

WITHDRAWN/CLOSED are explicit ended relationships, reflected as SKIP on that job.
CLOSED never infers accepted/declined/expired. Closed application records are not
edited/reopened; a new actual application is a new record. General event correction
and manual opportunities are not implemented; use a separately reviewed auditable
correction plan for a factual entry error.

## Verified checkpoint and results

Task 4 opened clean on main tracking origin/main at
574d7e2ce50cefe7273a9b957b8049a57908d766 (Task 3 checkpoint).
No remote query, staging, commit, push or tag was performed by the agent.
Task 4 is a prepared bounded checkpoint, not a completed Daily/Release Close.

Final test counts are recorded after verification: 30 focused Task 4 tests;
111 full-suite tests, including 20 Task 3 tests, all 27 Task 2 foundation tests
and four URL-security regressions. Existing tests changed only explicit schema
version/table expectations. All data/feeds/databases/reports in tests are synthetic
and temporary. Seven-job completeness and zero-coverage visibility remain verified.

Acceptance covers explicit applications, active suppression, new Controller
visibility, truthful sibling states, both rejection paths, unknown engagement,
withdrawal, offers, overrides, review resolution, multiple applications, restart
history, canonical multi-board identity, escaping, migration and rollback.
v2 migration preserves all old rows exactly; injected failure restores original
database bytes. v1 migration/rollback regressions remain passing.

No private database was opened, migrated or modified. Metadata-only checks found
no default database or sidecars before/after testing. No unrelated database search.
No new dependency, ATS, source registry, cost or external capability. SECURITY
was reviewed; existing local/private-data boundaries cover this change. No broad
security scan or live acceptance was performed. Final release security review
remains outstanding; prior URL remediation is not clearance for new code.

## Open work and exact next bounded task

Verify Adam's Task 4 checkpoint, branch/upstream and clean working-tree state.
Review remaining ROADMAP acceptance gaps with Adam and obtain a separately bounded
Task 5 scope before implementation. Do not research/select final employers,
migrate private history, rotate employers, build broader portfolio analytics or
export Excel without that separate authorization.

Remaining v1 work includes researched/approved final employer population, broader
portfolio/manual opportunities, employer replacement, optional private Excel
export, user/live acceptance and final security/release verification. v1 is not
complete. No unresolved Product Owner decision blocks the implemented Task 4 scope.

## Learning and governance

[WP-010](workpapers/WP-010.md) explains Task 4's machine, components and actual code.
Earlier workpapers retain historical context. OPERATING_SYSTEM now owns the
Product Owner / AI development gate and Automation Traceability Principle:
unknown is neither No nor Yes; execution success alone does not prove correctness.
