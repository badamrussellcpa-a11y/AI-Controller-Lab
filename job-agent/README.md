# Job Scout — current operating guide

## Current versus planned

The current local pilot has a validated employer registry, canonical employer
identity, explicit pool placement, schema v2, synthetic-tested migration and
observed source-run persistence. **Full v1 remains in progress**. The
[approved product contract](master_prompt.md) still plans the researched final
population, broad discovery, employer suppression, factual application portfolio
and optional private Excel export. Current Top 5
behavior remains intact; it is no longer the eventual product acceptance target.
Permanent close/recovery procedures live in
[OPERATING_SYSTEM.md](../OPERATING_SYSTEM.md), not this operating guide.

Fetches public Greenhouse employer feeds, screens accounting titles, applies the
weights in `search_rules.md`, and writes a readable shortlist plus a JSON snapshot.
No paid API, cloud database, extra Python packages, or application submissions.

## Run from the AI-Controller-Lab terminal

Fresh databases initialize schema v2. An existing legacy database deliberately
stops before fetching or updating jobs; it requires separately authorized migration
after private backup/restoration preparation (see below). Never delete history to
get past that stop. Task 2 did not migrate Adam's private database.

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

Open the newest `shortlist-*.md` in `job-agent/results/`. Each run creates a new
timestamped report. The accompanying JSON retains descriptions and evidence.
The existing `job_tracker.csv` is a separate manual tracker; its sample rows are
not inputs to this live search and are never overwritten.

## Options

- `--all-locations`: include target roles outside the initial location screen.
- `--boards rocketlab spacex`: choose explicitly registered ACTIVE board tokens.
  Unknown, BENCH or PAUSED sources now fail visibly instead of guessing identity.
- `--registry PATH`: use another validated JSON registry; default employers.json.
- `--limit 20`: override the default five-result shortlist to show at most 20 candidates.
- `--output PATH`: write snapshots to a different folder.
- `--state-file PATH`: use a different SQLite state file (parent folder must exist).
- `--mark JOB_ID STATE`: update a saved job without fetching feeds.
- `--history`: print all saved job records and their current states as JSON.
- `--migrate-state`: explicit existing-database schema migration only, no fetch;
  mutually exclusive with mark/history. Requires backup/restoration preparation
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
python .\job-agent\job_scout.py --mark "exampleboard:123" APPLIED
python .\job-agent\job_scout.py
python .\job-agent\job_scout.py --history
```

Replace the example ID with a real ID from your run. Marking a job records your
decision locally; it does not submit an application. Allowed states: `NEW`,
`SHORTLISTED`, `APPLIED`, `INTERVIEW`, `REJECTED`, `OFFER`, `SKIP`.
Only `NEW` and `SHORTLISTED` jobs qualify for fresh recommendations. Filtering
happens before the Top 5 limit, so other eligible jobs can fill the available
slots. Fewer than five is valid. Viewing a job does not change its state;
unhandled jobs may reappear. Use `--mark ID NEW` to deliberately reopen a job.

The default store is `job-agent/application_state.sqlite3`, independent of the
working directory and `--output`. Use the same `--state-file` for every command
when testing an alternative store. SQLite is included with Python; no dependency
or server is needed. Run these manual commands sequentially; a report reflects
state when it was selected, not status changes made after selection.

All fetched target-role records are retained, including those outside the location
filter, handled jobs, and jobs absent from later feeds. Each record keeps current
state, latest listing details, first/last seen times, and the last status-change
time. This is a current-state register, not a full log of every status transition.
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

## How to read results

- Score = matched signal weights / total weights, rounded to 0–100. Repeated
  keywords do not add extra points. This measures evidence coverage only.
- Candidates with excluded-topic mentions follow unflagged candidates, scores
  rank next, and your role priority breaks ties. Commute checks do not affect
  selection or ranking. The broad LA/remote location screen still applies.
- Finance Manager needs both an accounting signal and a leadership signal.
- Excluded terms in titles reject a job. Mentions in descriptions flag manual
  review because a keyword alone cannot establish the role's actual focus.
- The initial location screen recognizes selected LA-area city names and explicit
  remote locations. Remote does not establish California eligibility. The LA city
  list is incomplete; use `--all-locations` to inspect omitted roles.
- Pay is quoted as source excerpts, not converted into assumed annual base pay.
  Unknown pay is not zero. Your salary preference is shown but does not yet filter
  or boost a result. Non-dollar compensation needs manual review.
- Keywords can occur in qualifications, negations, or company boilerplate. Read the
  evidence and listing. Scores are not probabilities or final suitability judgments.
- Resume focus prompts suggest topics only; they do not invent your experience.

## Verify changes

```powershell
python -m unittest discover -s .\job-agent -p "test_*.py" -v
```

Substitute the verified interpreter path above if `python` is unavailable.
Tests cover false titles, weighted scoring, eligibility caveats, excluded-topic
review, duplicates, pay excerpts, out-of-area filtering, feed failures, persistent
states, all exclusion states, unknown IDs, reopening, absent-job retention,
transaction rollback, corrupt state, and Windows history output. Tests use
temporary databases and never modify your default application history.

## Employer registry and pool foundation — Task 2

employers.json is human-reviewed configuration, not employer research or executable
instructions. Its format version is 1 (separate from SQLite schema version 2).
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
No yield-based pool movement, application suppression or automatic rotation exists.

Optional text/null fields: approval_date, industry, size_band, company_stage_type,
la_evidence, remote_evidence, selection_rationale, research_reference,
research_checked_date and confidence_notes. Dates use YYYY-MM-DD when known.
Keep secrets, private contacts and application notes out of this tracked registry.
Approval labels record Adam's reviewed decision; software cannot confer approval.

Search startup synchronizes explicit configuration to SQLite. Removed entries/
mappings become configured=0, retaining their last pool placement and historical
jobs/observations. No history is deleted. Mark/history do not need the current
registry once the database is v2. A previously persisted board cannot be reassigned
to another employer by editing JSON; stop for a separately reviewed correction.

## Schema and migration foundation

SQLite PRAGMA user_version identifies the schema. The original jobs-only layout
is logical v1, recognized with user_version 0 (old unversioned files) or 1.
New databases use version 2: employers, employer_sources, jobs and source_runs.
Jobs retain all prior fields plus employer_id/source_board with foreign keys.
No portfolio or application-event tables have been added.

Normal run/mark/history commands refuse legacy migration. Unsupported versions,
unrecognized/partial layouts and integrity failures stop without resetting state.
Schema recognition is intentionally strict; an independently altered schema needs
review rather than an attempted best-effort migration.

Explicit migration copies existing IDs, states, raw snapshot text and all three
timestamps unchanged, mapping only source prefixes present in the supplied registry.
It never infers identity from company names or invents application dates/events.
DDL, copied records and version update share a transaction; any failure rolls back.
No source observations are backfilled. Running migration again on valid v2 is a no-op.

Before any future real migration: stop Scout, obtain explicit Adam authorization,
make an approved private SQLite-consistent backup (including any needed journal/WAL
state), establish a restoration plan and test restoration as appropriate. Rehearse
on an approved copy before touching the original. Git does not back up this data.
Do not run a migration on the real default database as part of Task 2.

For an existing **synthetic test database only**, the command shape is:

```powershell
python .\job-agent\job_scout.py --state-file "<synthetic-database-path>" --registry "<synthetic-registry-path>" --migrate-state
```

These are placeholders, not a command to paste against real history.

## Source-run observations

Each completed run stores one observation per attempted board: UTC attempt timestamp,
fetch success, count of normalized postings returned, count of unique currently
recognized target roles, and an error category on failure. Relevant counts are
before location, job-state and Top-5 filtering. Repeated IDs count once as relevant;
postings count reflects the fetched list. Invalid feed responses are failed fetches.

Successful empty feeds have zero counts; failures have NULL counts, never zero
yield. Only the exception class/category is persisted, not arbitrary error payloads.
Source mappings link observations to employers. Configuration/research notes remain
separate from observed facts. No earlier yield, employer scoring or rotation is
inferred. There is no analysis/export UI yet.

Job refreshes and source observations commit together. An interrupted process or
failed state write is not a completed observation batch; an old report is not proof
that the current run succeeded. Existing per-feed report health remains available.

## Task 2 verification — September 26, 2026

61 tests pass: 34 existing regressions and 27 focused registry/migration/observation
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
for run → mark APPLIED → rerun and verifies replenishment to five.

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
Primary Controller eligibility remains in the future discovery contract. Existing
evidence and resume-focus prompts remain current output; deeper candidate analysis
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

Current behavior (not the redesigned acceptance target): results are
capped at five by default, with fewer shown if fewer match. Commute links are
optional and there is no commute quota or commute-based sorting. Application-state
tracking now excludes handled jobs; fresh does not guarantee previously unseen.
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
