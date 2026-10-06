# AI Controller Lab — current recovery context

**Updated September 26, 2026. Task 5 committed; post-checkpoint learning reconciled; documentation-only Daily Close committed and pushed (5786e18). Release remains open.**

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

Task 5 is committed at aab64a2eab60c7337a59e9e6ac6540aeb67a4be2. Adam reports it
pushed and verified clean before this Daily Close. At preparation time, read-only Git
inspection confirmed main tracking origin/main, a clean starting tree, and HEAD/local
origin/main at that hash; no new remote query was made then. GitHub now confirms the
September 26 documentation-only Daily Close was committed and pushed at
5786e1867dc14b4266271e74cafb4f8719cc21b9 on main. This is not a Release Close.

At the Task 5 checkpoint, 28 focused foundation/configuration tests and all 112
tests passed, including 30
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

During Task 5, no private database was opened, migrated or modified; its metadata-only
checks found no default database/sidecars before or after those tests. This historical
observation is not a claim about state after Adam's later manual run. Task 5 introduced
no dependency, ATS, schema or external capability. SECURITY covered that configuration
change. Final release security review remains outstanding; prior URL remediation is
not clearance for later code. Today's documentation task accesses no application
database, changes no runtime/configuration/schema and does not rerun the test suite.
The 112-test result above is prior evidence, not today's execution.

## Post-checkpoint acceptance and learning

Adam reports running Scout with the verified interpreter after the Task 5 checkpoint:
**915 postings → 20 accounting-finance-v3 roles → 18 displayed → 18 unhandled by
job state within normal location policy**. All seven feeds were already reachable
in Task 5. The ignored local evidence is
job-agent/results/discovery-20260927-021901-686871.md; do not stage runtime output.
This close records supplied evidence, without repeating the run or reading private
state. Dated titles and interpretation are in job-agent/README.md.

Independent ChatGPT/Atlas public research found substantially the same useful role
population within these seven employers. Adam reviewed the possible Atlas-only
Figma Senior Technical Revenue Analyst difference and was not interested in that
role type; it does not warrant classifier expansion. Eighteen unhandled jobs does
not mean eighteen selection-eligible or geographically verified applications.

Scout demonstrates deterministic reduction/repeatability within its configured
Greenhouse universe. It does not demonstrate broader-market completeness or
commercial validation. Excellent employers on other systems are excluded. This
material business consequence was not adequately challenged early; it is a product/
architecture limitation, not a security defect or implementation failure.

The learning distinction is Atlas/reasoning AI → Codex/implementation agent →
deterministic Python/SQLite Scout. It became clear through the real project, not
through a tutorial planned that way from inception. The open value question is
whether repeatability/state/scale/control justify maintenance over AI-assisted
discovery. Successful implementation alone does not answer it.

## Open work and exact next bounded task

At the next session, inspect Git for changes since the verified documentation-only
Daily Close checkpoint (5786e1867dc14b4266271e74cafb4f8719cc21b9). Then review
whether Job Scout needs a final minimal closure/release disposition before shifting
focus. Inventory unresolved acceptance/security and any private-migration need
without opening private data; obtain an explicit scope disposition, not automatic
feature authorization. No v1 completion or Release Close is claimed here.

The next major Controller Lab direction is **AI Controller Capability Benchmark
planning**: define a cheap, bounded comparison of reasoning AI, existing tools and
a manual baseline, with common cases, measures and privacy boundaries. ROADMAP owns
the candidate tasks and measures. Do not implement the benchmark or automatically
start Bank Recon. Future substantial builds must pass the Build-vs-Existing
Capability Gate in OPERATING_SYSTEM.

Excel, broader portfolio/manual opportunities, multi-ATS work and automatic employer
rotation remain unapproved. Do not change the classifier for the reviewed Figma
difference, migrate private history, change the cohort, or add Job Scout features
without separately approved scope. There is no unresolved Task 5 source-mapping
issue; incremental value and final release disposition remain open.

## Learning and governance

[WP-012](workpapers/WP-012.md) explains the acceptance learning and resource distinctions.
[WP-011](workpapers/WP-011.md) preserves the Task 5 configuration checkpoint as written;
WP-010 preserves Task 4's machine/components/code. Historical workpapers are not
current next-task instructions. OPERATING_SYSTEM owns the integrated development/
Build-vs-Existing Capability Gate and traceability principle; FOUNDER_PROFILE records
professional learning preferences. Unknown remains unknown; execution success alone
does not establish correctness or incremental product value.
