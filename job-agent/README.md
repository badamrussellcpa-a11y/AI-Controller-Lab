# Job Scout — current operating guide

## Current versus planned

The current local pilot has a validated employer registry, canonical employer
identity, explicit pool placement, schema v3, synthetic-tested migration and
observed source-run persistence. Task 3 adds broad role classification and complete
employer-grouped discovery. Task 4 adds explicit application/event history,
derived employer suppression, reapply review, opportunity-specific overrides and
legacy reconciliation. **Full v1 remains in progress**. The
[approved product contract](master_prompt.md) still plans the researched final
population, broader strategic portfolio/manual opportunities and optional
private Excel export. Normal discovery no longer truncates to Top 5.
Permanent close/recovery procedures live in
[OPERATING_SYSTEM.md](../OPERATING_SYSTEM.md), not this operating guide.

Fetches public Greenhouse employer feeds, classifies accounting/finance titles,
collects informational weighted evidence from `search_rules.md`, and writes a
complete discovery report plus a JSON snapshot.
No paid API, cloud database, extra Python packages, or application submissions.

## Run from the AI-Controller-Lab terminal

Fresh databases initialize schema v3. An existing v1/v2 database deliberately
stops before fetching or updating jobs; it requires separately authorized migration
after private backup/restoration preparation (see below). Never delete history to
get past that stop. Tasks 2–4 did not migrate Adam's private database.

If Python is already available in your VS Code terminal:

```powershell
python .\job-agent\job_scout.py
```

The agent's terminal did not find `python` on PATH. This exact local Python runtime
was verified during the build and can be used instead:

```powershell
& 'C:\Users\Adam\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\job-agent\job_scout.py
```

This fallback belongs to the desktop app and may move after an app update. A normal
Python 3.10+ installation is sufficient; no dependency installation is needed.

Open the newest `discovery-*.md` in `job-agent/results/`. Each run creates a new
timestamped report. The accompanying JSON retains descriptions and evidence.
Older shortlist files are historical snapshots, not today's discovery contract.
The existing `job_tracker.csv` is a separate manual tracker; its sample rows are
not inputs to this live search and are never overwritten.

## Options

- `--all-locations`: also show explicitly incompatible locations for inspection.
  Ambiguous geography is already included normally with a location-review flag.
- `--boards rocketlab spacex`: choose explicitly registered ACTIVE board tokens.
  Unknown, BENCH or PAUSED sources now fail visibly instead of guessing identity.
- `--registry PATH`: use another validated JSON registry; default employers.json.
- `--limit`: retired; any supplied value produces an explicit error before
  database/network work. Remove it to obtain untruncated discovery.
- `--output PATH`: write snapshots to a different folder.
- `--state-file PATH`: use a different SQLite state file (parent folder must exist).
- `--mark JOB_ID STATE`: update a discovery label only, never create an application.
  APPLIED/INTERVIEW/OFFER/REJECTED labels require explicit legacy reconciliation.
  Jobs with explicit application history refuse --mark; use lifecycle commands.
- `--history`: print all saved job records and their current states as JSON.
- `--migrate-state`: explicit existing-database schema migration only, no fetch;
  mutually exclusive with all other actions. Requires backup/restoration preparation
  and explicit approval before use on real data.

Default pilot coverage: Rocket Lab, SpaceX, Figma, and Reddit. These are starter
data sources, not endorsements of employers or a complete market search. A board
can legitimately have zero target roles. Source failures are visible in the report.
Exit codes: 0 = all feeds succeeded; 1 = all feeds failed; 2 = partial feed failure.
Exit 3 means registry/state access or validation failed (including no ACTIVE
sources or a legacy schema needing explicit migration); no fresh report is
generated. Mark/history commands return 0 on success and 3 on failure.

## Application state and history

Run Scout normally, then copy the stable `board:job_id` from its report or console:

```powershell
python .\job-agent\job_scout.py
python .\job-agent\job_scout.py --record-application "exampleboard:123"
python .\job-agent\job_scout.py
python .\job-agent\job_scout.py --history
```

Replace the example ID with a saved ID and record only an application actually
submitted by you. Scout does not submit it. Job labels remain `NEW`,
`SHORTLISTED`, `APPLIED`, `INTERVIEW`, `REJECTED`, `OFFER`, `SKIP`.
Complete discovery includes handled jobs with their state and a “not a fresh
application recommendation” label. Only NEW/SHORTLISTED jobs within the broad
location policy appear in the JSON fresh_job_ids list and unhandled count.
That list is a job-state distinction, not verified actionability or employer
suppression. The normal selection list is now selection_job_ids, also shown in the
Markdown Application selection section. It additionally applies employer controls.
Viewing a job does not change its state. --mark ID NEW can reopen a discovery label
only when there is no explicit application record; it never clears legacy evidence.

The default store is `job-agent/application_state.sqlite3`, independent of the
working directory and `--output`. Use the same `--state-file` for every command
when testing an alternative store. SQLite is included with Python; no dependency
or server is needed. Run these manual commands sequentially; a report reflects
state when it was selected, not status changes made after selection.

All fetched target-role records are retained, including those outside the location
filter, handled jobs, and jobs absent from later feeds. Each record keeps current
state, latest listing details, first/last seen times, and the last status-change
time. This jobs table is still a current-state register; the separate application
events and employer decisions preserve explicit lifecycle history.
History adds a top-level employer_id; new report job records also carry employer_id.
Existing fields and stable board:job IDs remain. Migration preserves the original
snapshot text; a later fetch updates listing details as before.
Existing timestamped reports are preserved; old reports can still show a job that
you subsequently handled. Identity is based on the source ID; an employer repost
with a new ID is a new record. The separate sample CSV is not imported.

The database contains private application history. It and SQLite sidecars are
ignored by Git under the existing .sqlite3 patterns; custom report/history exports
must also remain private. A custom .db filename or .xlsx outside ignored results/
is not automatically protected by those patterns; verify exclusions before use. Back up
the database to an approved local location while Scout is closed. Git alone does
not back it up. Do not delete it to troubleshoot: that would lose saved exclusions.
A corrupt or inaccessible database stops the run rather than silently resetting
states. History JSON uses Unicode escapes for Windows console compatibility;
JSON readers recover the original text.

## Application lifecycle and employer controls — Task 4

The application record is authoritative for actual application facts. Discovery,
shortlisting and legacy --mark labels never establish an application. Record one
only when you actually applied; this local command does not submit anything.
The role snapshot and canonical employer/job links are captured at recording time.
Unknown submitted/event dates remain null, distinct from the UTC recording timestamp.
Dates may be YYYY-MM-DD or ISO timestamps with timezone; omit unknown values.

All action commands below operate on the explicitly chosen private state file and
fetch no feeds. Examples are synthetic command shapes, not facts about Adam. Use
real saved IDs only when deliberately recording your own facts. Keep reasons short
and free of contacts, secrets or unnecessary personal details; shell history may
retain typed arguments. Do not redirect history into a tracked file.

```powershell
# Set only to an authorized existing state file; this placeholder is not a real path.
$scoutState = '<authorized-private-state.sqlite3>'
python .\job-agent\job_scout.py --state-file $scoutState --record-application 'exampleboard:123'
# Use the application_id returned above (illustrative ID 1 below).
python .\job-agent\job_scout.py --state-file $scoutState --application-event 1 SCREEN
python .\job-agent\job_scout.py --state-file $scoutState --application-event 1 INTERVIEW
python .\job-agent\job_scout.py --state-file $scoutState --application-event 1 OFFER
python .\job-agent\job_scout.py --state-file $scoutState --applications
python .\job-agent\job_scout.py --state-file $scoutState --employer-status 'example-employer'
```

SCREEN covers a recruiter/HR screen; INTERVIEW covers hiring-manager/formal stages.
Both record meaningful engagement YES. An OFFER stays active until explicitly
closed; no acceptance/decline/expiry is inferred. APPLIED, SCREEN, INTERVIEW and
OFFER suppress normal sibling selection. Complete discovery still shows sibling
opportunities with **ACTIVE APPLICATION AT THIS EMPLOYER — REVIEW BEFORE SECOND
APPLICATION**. Their job states remain unchanged.

Closure requires a reason. Choose the appropriate command, not the entire sequence:

```powershell
# Only assert NO when you know no meaningful engagement occurred.
python .\job-agent\job_scout.py --state-file $scoutState --application-event 1 REJECTED --engagement NO --reason 'Synthetic pre-engagement rejection'
# After a recorded screen/interview, YES remains true without restating it.
python .\job-agent\job_scout.py --state-file $scoutState --application-event 1 REJECTED --reason 'Synthetic hiring process ended'
python .\job-agent\job_scout.py --state-file $scoutState --application-event 1 WITHDRAWN --reason 'Synthetic withdrawal'
python .\job-agent\job_scout.py --state-file $scoutState --application-event 1 CLOSED --reason 'Synthetic offer relationship ended'
```

REJECTED means rejection, WITHDRAWN means user-recorded withdrawal, CLOSED means an
explicitly ended relationship without asserting a more specific outcome. CLOSED
does not mean accepted, declined or expired. These events end that application.
With engagement NO, closure removes that application's restriction. YES or UNKNOWN
requires REVIEW BEFORE REAPPLYING. Unknown is never silently converted to No.
Prior YES cannot be erased by a later NO. Closing one application leaves other
active/review/legacy restrictions intact. No cooling-off timer exists.

An application command changes only its own job label: application → APPLIED;
SCREEN/INTERVIEW → INTERVIEW; OFFER → OFFER; REJECTED → REJECTED; WITHDRAWN/CLOSED →
SKIP (handled, not a fabricated rejection). The authoritative outcome stays in the
application events. Closed applications cannot be silently reopened or edited;
another actual application is a new record. The interface does not implement
general event correction/backdating reconstruction. Stop for a separately reviewed
auditable correction if an application event was entered incorrectly.

```powershell
python .\job-agent\job_scout.py --state-file $scoutState --authorize-opportunity 'example-employer' 'exampleboard:456' --reason 'Synthetic approval to consider this sibling role'
python .\job-agent\job_scout.py --state-file $scoutState --resolve-reapply-review 'example-employer' --reason 'Synthetic context review completed; reconsideration approved'
```

An override requires the canonical employer, an unhandled saved sibling job and a
nonblank reason. It records a timestamp and authorizes consideration only; it never
submits an application or marks a job APPLIED. No employer-wide bypass or timer is
created. It survives restart and ordinary active-stage progression. New applications,
closures or reconciliation/review decisions change the restriction context and
require fresh authorization. Changes to the authorized listing's title, location,
description or URL also require fresh authorization, conservatively including text
edits that may not ultimately be material. Unchanged refreshes preserve authorization.
Prior decisions remain in history when no longer applicable. Their context_evidence
shows restriction/event references and the authorized listing snapshot, not an
unexplained opaque flag.

Resolving review clears only the currently identified review facts and appends a
reason/timestamp; it cannot clear an active application or unreconciled legacy facts.
New unsuccessful engaged processes require new review. Recording an actual second
application is permitted as a factual action even if selection policy discouraged it:
the system must record reality, not hide it. Duplicate active records for the same
job are refused. No command autonomously applies or communicates.

## Legacy application reconciliation

Migration preserves all original job states, snapshots and timestamps. Legacy
APPLIED/INTERVIEW/OFFER/REJECTED labels are copied into a separate fact register;
no application, date, screen, interview, engagement or rejection timing is inferred.
REJECTED is included because the old label cannot distinguish the two rejection
paths. An employer with unresolved legacy facts is RECONCILIATION REQUIRED and
excluded from selection, while complete discovery remains visible. A later --mark
NEW or a job-specific override cannot bypass this gate.

Choose one explicit disposition per legacy job, with a reason:

```powershell
python .\job-agent\job_scout.py --state-file $scoutState --reconcile-legacy 'example-employer' 'exampleboard:123' --disposition ELIGIBLE --reason 'Synthetic current eligibility explicitly reviewed'
python .\job-agent\job_scout.py --state-file $scoutState --reconcile-legacy 'example-employer' 'exampleboard:123' --disposition REVIEW --reason 'Synthetic context requires reapply review'
python .\job-agent\job_scout.py --state-file $scoutState --reconcile-legacy 'example-employer' 'exampleboard:123' --disposition LINKED --application-id 1 --reason 'Synthetic legacy label reconciled to independently recorded application'
```

ELIGIBLE is a current human disposition, not a claim that historical engagement was
NO. REVIEW imposes reapply review without fabricating history. LINKED requires an
explicit application for the same job; record only facts you can affirm, retaining
unknown dates/engagement. All legacy jobs must be reconciled individually. Later
decisions supersede earlier dispositions visibly; old facts/decisions remain.
Reconciliation never changes the legacy job label. Other application restrictions
still apply. Pool placement stays independent.

## Task 4 verification — September 26, 2026

Focused lifecycle/migration tests and the full regression suite use only synthetic
temporary databases and simulated feeds. See BOOT_CONTEXT for final counts.
Coverage includes explicit facts/unknowns, active suppression with all seven fixture
jobs visible, both rejection paths, engaged withdrawal, unresolved offers, scoped
override/review decisions, restart history, legacy reconciliation, v2 migration and
transaction rollback. Existing v1 migration, discovery and URL-security checks remain.
No private database was accessed/migrated, no dependency was added, and no external
action or broad security scan was performed. Final live/security/release gates remain.

## How to read results

- Accounting-signal coverage = matched signal weights / total weights, rounded
  to 0–100. Each signal counts once. It never gates inclusion, sorting or a limit,
  and is not hiring probability, candidate fit or job quality.
- Reports group by canonical employer (display-name order, then employer ID).
  Within each employer: CLEAR MATCH first, then REVIEW NEEDED, family display
  order, title and stable ID. Pay, coverage and commute do not control order.
- CLEAR MATCH means an approved primary title family, including Controller,
  Assistant Controller, Accounting Manager variants and Senior Accountant.
  REVIEW NEEDED covers senior/management adjacent families (FP&A, treasury, tax,
  audit, payroll, AP/AR and finance leadership), ambiguous scope and review flags.
- Finance Manager and credit/accounting operations use a separate description
  scope check: accounting/finance responsibility terms, not numeric coverage.
  Missing descriptions remain REVIEW NEEDED; nonempty descriptions without that
  scope are excluded for those ambiguous families.
- Excluded terms in titles reject a job. Mentions in descriptions flag manual
  review because a keyword alone cannot establish the role's actual focus.
- Recognized LA-area/hybrid and explicit California/nationwide remote labels
  surface normally. Ordinary Remote/US, unknown cities and mixed remote-region
  labels stay visible as REVIEW NEEDED — LOCATION. Explicit outside-area state/
  region labels and California exclusions are omitted normally, retained in
  history, and visible with --all-locations. Rules are conservative heuristics,
  not geocoding or verified eligibility; no commute time is inferred.
- Pay is quoted as source excerpts, not converted into assumed annual base pay.
  Unknown pay is not zero. Your salary preference is shown but does not yet filter
  or boost a result. Non-dollar compensation needs manual review.
- Keywords can occur in qualifications, negations or boilerplate. Read the source
  evidence. Adam + ChatGPT handle strategic fit, application writing and interviews.

Title exclusions retain unrelated controller/engineering/product/sales uses,
junior/staff/clerk/bookkeeper/intern roles and excluded lending/insurance topics.
See search_rules.md for family order, topic list and explanation; job_scout.py
holds the deterministic patterns. No deterministic classifier guarantees perfect
recall. Complete means no Top-N hiding of the population recognized by these rules.

The report shows source health for every selected board and employer sections
even when no roles are displayed. Any failed or deliberately unsearched ACTIVE
board makes source coverage INCOMPLETE. A successful empty source is reported
separately from failure; --boards is explicitly a subset when applicable.

JSON retains a flat, employer-ordered jobs list and adds employer metadata,
fresh_job_ids, coverage_complete, active_source_count, excluded_location_count and
discovery_policy=accounting-finance-v3. Per-job review_status is CLEAR MATCH or
REVIEW NEEDED, with classification_reason and location_classification.
The old score key is replaced by accounting_signal_coverage. Existing historical
snapshots are not rewritten; refreshed listing JSON acquires the new fields.
Task 3 introduced no schema change. Task 4 uses schema v3 and adds application_policy=
lifecycle-v4, selection_job_ids, per-job selection_eligible/selection_reason and
employer relationship evidence. fresh_job_ids is retained for compatibility and
must not be mistaken for the controlled selection queue.

## Verify changes

```powershell
python -m unittest discover -s .\job-agent -p "test_*.py" -v
```

Substitute the verified interpreter path above if `python` is unavailable.
Tests cover false titles, weighted scoring, eligibility caveats, excluded-topic
review, duplicates, pay excerpts, out-of-area filtering, feed failures, persistent
states, handled-state labeling, unknown IDs, reopening, absent-job retention,
transaction rollback, corrupt state, and Windows history output. Tests use
temporary databases and never modify your default application history.

## Employer registry and pool foundation — Task 2

employers.json is human-reviewed configuration, not employer research or executable
instructions. Its format version is 1 (separate from SQLite schema version 3).
The shipped entries are Rocket Lab, SpaceX, Figma and Reddit, all ACTIVE/PILOT,
not Adam's final approved Top 10. No employer statistics were researched.

Each entry requires employer_id, display_name, greenhouse_boards (one or more
explicit tokens), approval_status and pool. Canonical IDs use lowercase letters/
digits/hyphens, start with a letter and are at most 64 characters. They are stable
identity keys, independent of names, board tokens and job IDs. A display-name
change retains identity; no parent/subsidiary/name-based grouping occurs.
Duplicate IDs, duplicate JSON keys, ambiguous board mappings (including case-only
duplicates), invalid tokens and unknown fields fail validation.

Approval status is PILOT, APPROVED, PENDING or REJECTED. PENDING/REJECTED entries
must be PAUSED. Multiple boards belong to the same employer only through explicit
reviewed mappings. ACTIVE sources with PILOT/APPROVED status are fetched by default;
BENCH/PAUSED are retained but not fetched, including through --boards. Fewer than
ten ACTIVE employers is valid and the report shows the configured count.
No yield-based pool movement or automatic rotation exists. Application relationship
is derived separately; it never changes ACTIVE/BENCH/PAUSED pool placement.

Optional text/null fields: approval_date, industry, size_band, company_stage_type,
la_evidence, remote_evidence, selection_rationale, research_reference,
research_checked_date and confidence_notes. Dates use YYYY-MM-DD when known.
Keep secrets, private contacts and application notes out of this tracked registry.
Approval labels record Adam's reviewed decision; software cannot confer approval.

Search startup synchronizes explicit configuration to SQLite. Removed entries/
mappings become configured=0, retaining their last pool placement and historical
jobs/observations. No history is deleted. Mark/history do not need the current
registry once the database is v3. A previously persisted board cannot be reassigned
to another employer by editing JSON; stop for a separately reviewed correction.

## Schema and migration foundation

SQLite PRAGMA user_version identifies the schema. The original jobs-only layout
is logical v1, recognized with user_version 0 (old unversioned files) or 1.
Version 2 introduced employers, employer_sources, jobs and source_runs.
Jobs retain all prior fields plus employer_id/source_board with foreign keys.
Version 3 adds applications, application_events, legacy_application_facts and
employer_decisions. No broader portfolio analytics or manual opportunities exist.

Normal commands refuse v1/v2 migration. Unsupported versions,
unrecognized/partial layouts and integrity failures stop without resetting state.
Schema recognition is intentionally strict; an independently altered schema needs
review rather than an attempted best-effort migration.

Explicit migration copies existing IDs, states, raw snapshot text and all three
timestamps unchanged, mapping only source prefixes present in the supplied registry.
It never infers identity from company names or invents application dates/events.
DDL, copied records and version update share a transaction; any failure rolls back.
No source observations are backfilled. v2-to-v3 adds tables and copies application-
related legacy labels as evidence, without changing old rows or inventing application
events. v1-to-v3 uses the existing canonical mapping then captures the same labels.
Running migration again on valid v3 is a no-op.

Before any future real migration: stop Scout, obtain explicit Adam authorization,
make an approved private SQLite-consistent backup (including any needed journal/WAL
state), establish a restoration plan and test restoration as appropriate. Rehearse
on an approved copy before touching the original. Git does not back up this data.
Do not run a migration on the real default database as part of Task 4.

For an existing **synthetic test database only**, the command shape is:

```powershell
python .\job-agent\job_scout.py --state-file "<synthetic-database-path>" --registry "<synthetic-registry-path>" --migrate-state
```

These are placeholders, not a command to paste against real history.

## Source-run observations

Each completed run stores one observation per attempted board: UTC attempt timestamp,
fetch success, count of normalized postings returned, count of unique currently
recognized accounting/finance roles, and an error category on failure. Relevant
counts are before location filtering and independent of job state. Repeated IDs count once as relevant;
postings count reflects the fetched list. Invalid feed responses are failed fetches.
Task 3 broadens the recognition policy. Older narrow-policy observations are not
rewritten and should not be compared as if the definition of relevant never changed.
New reports identify the discovery policy; source-run tables/schema stay unchanged.

Successful empty feeds have zero counts; failures have NULL counts, never zero
yield. Only the exception class/category is persisted, not arbitrary error payloads.
Source mappings link observations to employers. Configuration/research notes remain
separate from observed facts. No earlier yield, employer scoring or rotation is
inferred. There is no analysis/export UI yet.

Job refreshes and source observations commit together. An interrupted process or
failed state write is not a completed observation batch; an old report is not proof
that the current run succeeded. Existing per-feed report health remains available.

## Historical Task 3 verification — September 26, 2026

81 tests pass: 20 focused discovery tests plus 61 retained/adapted regressions.
All 27 registry/migration tests and four URL-security tests pass. Fixtures verify
primary/adjacent/excluded roles, seven zero-coverage jobs all visible, canonical
employer grouping, stable non-score ordering, retired --limit, ambiguous/incompatible
geography, all seven truthful states, source-failure/subset disclosure and escaped
external headings/context. Existing Top-5 test expectations were deliberately
updated to complete-discovery expectations, not silently dropped.

No new live-feed acceptance or broad security scan was performed. All test state
is synthetic/temporary; no private application database was opened or modified.
The database schema, registry entries, dependency footprint and SECURITY policy
remain unchanged. v1 acceptance/release remains open.

## Historical Task 2 verification — September 26, 2026

61 tests passed: 34 existing regressions and 27 focused registry/migration/observation
tests. Migration tests use synthetic temporary databases, preserve original values,
and verify byte-for-byte rollback after unmapped identities and injected failure.
Separate-process tests verify persistence and handled-state exclusion. Four-pilot
integration uses simulated feed input; no new live acceptance or security scan
is claimed. No private application database was opened, migrated or modified.
Full v1 acceptance remains open.

## Historical verification — September 25, 2026 (Pacific)

Historical checkpoint evidence: 34 tests passed (22 original, eight persistence,
four URL-security). The standard Codex Security scan completed with one low-severity
application-URL/Markdown injection finding. The targeted fix validates URLs at
ingestion and revalidates/encodes them at Markdown output; focused tests passed.
This is not a subsequent full scan or security clearance for planned changes.
Task 1 on September 26 changed documentation only; it did not rerun this suite or
live acceptance. A deterministic acceptance test uses separate Python processes
for run → mark APPLIED → rerun formerly verified replenishment to five; Task 3's
updated contract verifies preserved visibility/state and exclusion from unhandled IDs.

Live acceptance also passed with an isolated test database: four feeds succeeded
on both runs, returning 3,428 postings and nine target-role records. The first
shortlist had five jobs. Marking `rocketlab:7784096003` APPLIED removed it on rerun,
leaving four eligible recommendations. All nine historical records remained;
the selected job was still fetched and retained its APPLIED state. No real
application was submitted and the default state database was not changed.
Local evidence is in ignored
`results/v1-acceptance-20260926-000157/acceptance.json` with first/second reports.
The initial sandbox attempt could not access the network; the approved live retry
succeeded. History display initially exposed a Windows encoding issue, now fixed
and covered by a regression test; persisted state and filtering were correct.

Full v1 remains open under the [redesigned acceptance gates](../ROADMAP.md).
Historically, live Controller coverage and application-ready summary acceptance
were unverified; the run contained Senior Accountant and Accounting Manager roles.
Runtime application-ready summaries/resume bullets/recruiter messages and
algorithmic Top 5 are now superseded requirements, not retroactively passed tests.
Primary Controller eligibility is now fixture-tested in broad discovery. Evidence
remains current output; runtime resume-focus prompts were removed. Deeper candidate analysis
belongs to Adam + ChatGPT. No release is declared.

`browser.py` and `browser_test.py` remain earlier browser experiments; they are not
needed for this version. The former heading-only scraper has been replaced.

Source contract: [Greenhouse Job Board API](https://docs.greenhouse.io/job-board.html).
Public GET endpoints need no authentication; `content=true` includes descriptions.

## Commute review

`search_rules.md` now contains the confirmed driving origin and 45-minute limit
each way. Reports include morning and return Google Maps links. These links do
not supply travel times to the program and need no mapping subscription. Open a
link, confirm the actual office, and check expected weekday arrival/departure
times. With a travel-time range, use the upper bound for conservative planning.

Current discovery is untruncated. Commute links are optional, with no commute quota
or commute-based sorting. Application-state tracking labels handled jobs truthfully;
the separate unhandled-job IDs do not guarantee previously unseen opportunities.
Runs remain manual.

To retain a checked route, ask the assistant to record the estimates and office
address. The optional local `commute_reviews.json` is keyed by job ID from the
report's JSON snapshot. Its format is:

```json
{
  "exampleboard:123": {
    "origin": "Hollywood Blvd and N Vista St, Los Angeles, CA",
    "mode": "driving",
    "listing_location": "Exact location text from the job",
    "office_address": "Verified office address",
    "checked_on": "2026-09-25",
    "arrival_time": "Weekdays 9am",
    "leave_work_time": "Weekdays 5pm",
    "outbound_minutes": 40,
    "return_minutes": 45
  }
}
```

The example is illustrative, not a checked commute. No review file is created
until a route is actually checked. Reviews older than 30 days, from a different
origin or mode, or attached to a changed listing location require rechecking.
Saved estimates can indicate whether both directions meet the preference, but
they never lower a job's rank or prevent it appearing in the shortlist.
Even recorded route estimates are not guarantees. Reconfirm office attendance
and worksite details with the employer, especially for hybrid/multi-office roles.

Maps link reference: [Google Maps URLs](https://developers.google.com/maps/documentation/urls/get-started).
