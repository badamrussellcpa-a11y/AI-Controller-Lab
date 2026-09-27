# AI Controller Lab — current recovery context

**Updated September 26, 2026. Task 5 cohort configured; Job Scout v1 remains in progress.**

Permanent procedures: [OPERATING_SYSTEM.md](OPERATING_SYSTEM.md).
Security: [SECURITY.md](SECURITY.md). Product: [job-agent/master_prompt.md](job-agent/master_prompt.md).
Acceptance: [ROADMAP.md](ROADMAP.md). Commands: [job-agent/README.md](job-agent/README.md).

## Current machine

Task 5 configures the Product Owner-approved ACTIVE cycle of seven: Muck Rack,
LaunchDarkly, BaubleBar, Airtable, Figma, Reddit and Rocket Lab. All seven are APPROVED;
SpaceX retains emp-spacex/spacex as PAUSED with historical PILOT metadata. Existing
Rocket Lab/Figma/Reddit IDs are unchanged. employers.json owns the exact mappings.
ACTIVE is a cycle decision, not a Top-10 quota. Human + AI research informs Adam;
Scout executes the configuration without an employer-scoring algorithm. No private
selection reasons or speculative bench entries. Future cohorts require new approval.

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

Task 5 opened clean on main tracking origin/main at
0159b0e46a388d93b4383af7efdba3885595a6da (Task 4 checkpoint).
No remote query, staging, commit, push or tag was performed by the agent.
Task 5 is a prepared bounded checkpoint, not a completed Daily/Release Close.

28 focused foundation/configuration tests and all 112 tests pass, including 30
Task 4 lifecycle tests, 20 Task 3 tests and four URL-security regressions. The two
production-registry expectations now describe seven approved sources; a new test
proves pausing SpaceX preserves job/application/source history. All automated tests
use synthetic temporary data. Discovery rules and schema remain unchanged.

Bounded live check at 2026-09-27 01:52:57 UTC (September 26 Pacific): all seven
fetches succeeded through the existing fetch_jobs/evaluate functions. 915 postings,
20 recognized accounting/finance roles before location/state/employer filters.
Counts by source and public mapping references are in job-agent/README.md. Airtable
returned three postings and zero recognized roles; zero is not a source failure.
Ignored aggregate evidence: job-agent/results/task5-source-check-20260927-015258.json.
The earlier sandbox attempt failed with URLError and null counts; approved network
retry succeeded. Live validation opened/created no database and followed no individual
application links. It is compatibility evidence, not final usefulness acceptance.

Acceptance covers explicit applications, active suppression, new Controller
visibility, truthful sibling states, both rejection paths, unknown engagement,
withdrawal, offers, overrides, review resolution, multiple applications, restart
history, canonical multi-board identity, escaping, migration and rollback.
v2 migration preserves all old rows exactly; injected failure restores original
database bytes. v1 migration/rollback regressions remain passing.

No private database was opened, migrated or modified. Metadata-only checks found
no default database or sidecars before/after testing. No unrelated database search.
No new dependency, ATS, schema, cost or external capability. SECURITY was reviewed;
existing public-feed/local-data controls cover this configuration change. No broad
security scan or final user acceptance was performed. Final release security review
remains outstanding; prior URL remediation is not clearance for new code.

## Open work and exact next bounded task

Verify Adam's Task 5 checkpoint, branch/upstream and clean working-tree state.
Obtain a bounded Product Owner acceptance-comparison plan for Scout versus separate
ChatGPT/manual research of the same seven approved employers, using isolated state
and preserving source/date evidence. Do not change the cohort, expand ATS support,
migrate private history, build portfolio/Excel features or perform Release Close
without separate authorization.

Remaining work: Product Owner usefulness acceptance, optional minimal portfolio/
Excel layer, any authorized real/private migration, final security review and
Release Close. Future cohorts require separate approval. v1 is not complete.
No unresolved source-mapping or Product Owner issue blocks Task 5 configuration.

## Learning and governance

[WP-011](workpapers/WP-011.md) explains the Task 5 cohort/configuration boundary.
WP-010 explains Task 4's machine, components and actual code.
Earlier workpapers retain historical context. OPERATING_SYSTEM now owns the
Product Owner / AI development gate and Automation Traceability Principle:
unknown is neither No nor Yes; execution success alone does not prove correctness.
