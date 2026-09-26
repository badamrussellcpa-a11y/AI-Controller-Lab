# AI Controller Lab — current recovery context

**Updated September 26, 2026. Job Scout v1 remains in progress.**

Permanent recovery/Daily Close/Release Close: [OPERATING_SYSTEM.md](OPERATING_SYSTEM.md).
Security: [SECURITY.md](SECURITY.md). Product: [job-agent/master_prompt.md](job-agent/master_prompt.md).
Acceptance: [ROADMAP.md](ROADMAP.md). Commands: [job-agent/README.md](job-agent/README.md).

## What exists

Task 2 adds a standard-library JSON employer registry with explicit canonical IDs,
reviewed Greenhouse mappings and ACTIVE/BENCH/PAUSED placement. The four employers
remain ACTIVE/PILOT sources, not the approved final Top 10. No automatic rotation.

SQLite schema v2 stores employers, source mappings, existing job state linked to
canonical identity and observed source-run facts. Failures have null yield counts;
successful zero yield is distinct. No historical observations are fabricated.
Configuration removal retains historical records; persisted source reassignment
fails rather than guessing identity.

Explicit transactional migration recognizes the original jobs-only schema as v1
(user_version 0 or 1), preserving IDs, states, snapshots and timestamps. Normal
run/mark/history commands stop on legacy schema; migration is a separate opt-in.
No private database was opened or migrated. A filename-only check found no default
application_state.sqlite3 or sidecars at the expected path before/after testing;
no search for private databases elsewhere was performed.

The original role/location/scoring/Top-5 pipeline and seven job states remain.
Only NEW/SHORTLISTED qualify for fresh recommendations. URL validation and Markdown
hardening remain unchanged. Browser scripts and sample CSV are separate artifacts.

## Verified checkpoint and results

Task 2 opened clean on main tracking origin/main at
6ab7fac1a4ff8d6845a2ef9f96bdc669c716a381 (Task 1 documentation checkpoint).
Remote state was not queried. Task 2 commit/push is left to Adam; verify later HEAD
and remote state from Git rather than assuming a checkpoint succeeded.

61 automated tests pass: 34 original regressions plus 27 focused foundation tests.
Evidence includes synthetic legacy migration, byte-for-byte rollback after late
failure, future/partial schema refusal, preserved snapshots/timestamps, explicit
source identity, no automatic pool movement, restart persistence, null failed-fetch
yield and simulated four-pilot integration. All test databases/reports are temporary.

Diff/scope/privacy checks accompany the checkpoint; no dependencies or broad
security scan were added. Current SECURITY policy covers configuration as data,
parameterized SQL, least privilege and approval for real-data migration; no policy
change was needed. Historical security scan/URL remediation and live APPLIED
acceptance remain recorded in the operating README and WP-006; no new live test
or redesigned release acceptance is claimed.

## What remains open

The final researched/approved Top 10 and bench, broad discovery, employer active-
application suppression, portfolio, recruiter/manual opportunities, diversification
analysis and Excel export remain planned. Job history is still a latest-state
register, not a complete application event journal. No application-writing runtime
feature is required. Real migration requires an approved private backup,
restoration plan/test as appropriate and explicit Adam authorization.
Do not delete a database or casually remap a source to bypass a failure.

## Exact next-session task

Verify Adam's Task 2 checkpoint and clean working-tree state. Review the completed
registry/migration foundation and obtain Adam's bounded Task 3 scope before further
implementation. Do not research/select final employers, migrate real application
data, broaden discovery, add employer suppression, portfolio or Excel export
without that separate authorization.

## Learning context

[WP-008](workpapers/WP-008.md) explains Task 2 from the plain-English machine to
components and actual code patterns. Earlier workpapers are historical learning
records, not competing current requirements or permanent procedures.
