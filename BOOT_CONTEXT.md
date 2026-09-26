# AI Controller Lab — current recovery context

**Updated September 26, 2026. Job Scout v1 remains in progress.**

Permanent recovery and close procedures live only in
[OPERATING_SYSTEM.md](OPERATING_SYSTEM.md). Product authority:
[job-agent/master_prompt.md](job-agent/master_prompt.md); acceptance:
[ROADMAP.md](ROADMAP.md); current commands: [job-agent/README.md](job-agent/README.md).

## What exists

The working pilot uses scraper.py (public Greenhouse ingestion), job_scout.py
(deterministic screening/scoring and default Top 5 Markdown/JSON reports), and
application_state.py (local SQLite job-state register). Rocket Lab, SpaceX,
Figma and Reddit are technical pilot sources, not the approved final employer pool.
Only NEW/SHORTLISTED jobs appear in fresh recommendations. All saved target-role
records remain, including handled/absent jobs; storage is latest state, not a
complete application event history. Browser scripts and the sample CSV are
separate legacy/manual artifacts.

Task 1 updated specifications and governance only. Approved registry, broad
discovery, employer suppression, factual portfolio and private Excel export remain
planned. No code/schema/data migration, employer selection or new dependency was
part of Task 1. Old Top-5/application-writing requirements are superseded.

## Verified checkpoint and limits

At Task 1 opening, local HEAD was 93264d0, branch main tracking origin/main,
with a clean tree and no local tags. Remote state was not queried this task.
Identify any later checkpoint from Git; do not treat this prior hash as current.

Recorded September 25 evidence: 34 Job Scout tests passed; standard security scan
completed with one low-severity URL/Markdown issue; targeted fix and regression
tests passed. Ingestion validates URLs; report output revalidates/encodes them.
No subsequent full security scan is claimed.

Recorded isolated live acceptance: four feeds, 3,428 postings, nine target roles;
marking one APPLIED reduced five recommendations to four while retaining its
state/history. This tested job-level exclusion, not planned employer suppression.
Private acceptance artifacts are not part of a fresh clone; see the operating
README and dated WP-006 for recorded evidence.

Task 1 verification checks documentation scope, diff whitespace and unchanged
runtime-parsed search rules. Runtime tests and live acceptance were not rerun.
No v1 release is established. Task 1's commit/push is left to Adam; confirm it
from Git at the next opening rather than assuming completion.

## Open items and decisions

All redesigned acceptance gates remain open. Initial Top 10 and bench need research
and Adam approval. Canonical identity, migration safety, application lifecycle
(including withdrawal/closure and resolved offers), override semantics and export
security need bounded implementation/testing. Preserve existing private history.
No commute times are newly verified. No runtime application-writing feature is
required. No new security scan or real database access occurred in Task 1.

## Exact next-session task

Verify Adam's Task 1 documentation checkpoint and working-tree state. Then, only
under a separately authorized Task 2, review the minimum employer-registry and
canonical-identity design, including a versioned SQLite migration and tests using
synthetic legacy records, before implementing that bounded foundation. Do not
research/select the final employers, migrate real application data, or implement
broad discovery, employer suppression, portfolio or Excel export in that task
without explicit scope approval.

## Learning context

[WP-007](workpapers/WP-007.md) explains this documentation/governance checkpoint
and the actual machine. Earlier workpapers are dated history, not competing
current product requirements or operating procedures.
