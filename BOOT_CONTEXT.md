# AI Controller Lab — current recovery context

**Updated September 26, 2026. Task 3 implemented; Job Scout v1 remains in progress.**

Permanent procedures: [OPERATING_SYSTEM.md](OPERATING_SYSTEM.md).
Security: [SECURITY.md](SECURITY.md). Product: [job-agent/master_prompt.md](job-agent/master_prompt.md).
Acceptance: [ROADMAP.md](ROADMAP.md). Commands: [job-agent/README.md](job-agent/README.md).

## What exists

Task 3 changes the discovery/output contract: search explicitly mapped ACTIVE
Greenhouse sources, classify primary accounting titles CLEAR MATCH and adjacent
senior/management finance families REVIEW NEEDED, preserve reasons/evidence, and
show all recognized broadly location-eligible roles grouped by canonical employer.
No Top-5 gate remains; --limit fails with a retirement message before state/network
work. Coverage and pay do not control inclusion or order.

Unknown locations remain visible for review. Explicit outside-area locations are
retained in history and inspectable with --all-locations. No commute times or
California eligibility are invented. Complete discovery includes handled jobs with
truthful state labels; fresh_job_ids contains only NEW/SHORTLISTED within the
location policy and means unhandled, not verified actionability.

Reports are discovery-*.md/.json. JSON uses accounting_signal_coverage rather than
score, and includes classification_reason, location_classification, employer
metadata and explicit source coverage. Failed or unsearched ACTIVE sources make
coverage incomplete. Current source-run counts reflect the broader rules; older
observations are retained without rewriting their narrower historical meaning.

Task 2's four ACTIVE/PILOT registry entries, canonical identity, explicit pools,
source mappings, schema v2, opt-in transactional migration and source observations
remain. No automatic rotation or employer application suppression. SQLite job
state is still a latest-state register, not application event history.

## Verified checkpoint and results

Task 3 opened clean on main tracking origin/main at
364d49bea8a4a93b21dd481b4eab3c85eb3915fd (Task 2 checkpoint).
No remote query, commit, push or tag was performed in Task 3. Verify Adam's later
checkpoint from Git; this document does not claim its own future commit hash.

81 tests pass: 20 focused discovery tests and 61 retained/adapted regressions,
including all 27 registry/migration tests and four URL-security tests. More-than-
five acceptance includes seven zero-coverage roles at one employer, all displayed
in Markdown/JSON. Tests also cover canonical grouping, deterministic non-coverage
ordering, truthful handled states, source-failure/subset disclosure, review-needed
locations and escaping of external headings/context.

Old Top-5/ranking assertions were changed explicitly to match the approved Task 3
contract; preserved state/migration/security assertions still pass. All test files,
databases and reports use synthetic data and temporary locations.

No private database was opened, migrated or modified; a filename/metadata check
found no default database/sidecars at the expected path before/after tests.
No search outside that path was performed. No schema, registry entries, dependencies
or SECURITY-policy changes. No broad security scan or live-feed acceptance;
historical evidence remains in the operating README and earlier workpapers.

## Open items

Final researched/approved Top 10 and bench, employer active-application suppression,
portfolio, manual/recruiter opportunities, controlled employer replacement, Excel
export, strategic application analysis and final live acceptance/release remain
planned. Title/location rules are deterministic heuristics, not perfect recall,
geocoding or candidate judgment. Review real usefulness at a later authorized gate.

Future private migration still requires explicit Adam authorization, approved
private backup and restoration plan/test as appropriate. Normal commands refuse
legacy auto-migration. Do not delete history to bypass a failure.

## Exact next bounded task

Verify Adam's Task 3 checkpoint and clean working-tree state. Obtain a bounded
Task 4 authorization for employer active-application suppression using canonical
identity and truthful job states; review closure/withdrawal, offer resolution,
override and history-preservation requirements before implementation. Do not
migrate private data, research final employers, build the portfolio or export
Excel without separate authorization.

## Learning context

[WP-009](workpapers/WP-009.md) explains Task 3's machine, components and real code
patterns. WP-007/WP-008 preserve earlier learning/history, not current Top-5 rules.
This is a bounded Task 3 checkpoint preparation, not a claim of final Daily Close
or v1 Release Close.
