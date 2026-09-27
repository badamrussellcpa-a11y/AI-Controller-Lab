# AI Controller Lab Roadmap

**Job Scout: working system with scoped acceptance evidence; value/closure review next; release remains open.**
The [product contract](job-agent/master_prompt.md) owns detailed requirements.
[OPERATING_SYSTEM.md](OPERATING_SYSTEM.md) owns Daily Close and Release Close.

## Current baseline and evidence

Implemented: seven Product Owner-approved ACTIVE Greenhouse sources, broad deterministic classification,
informational accounting-signal coverage, untruncated employer-grouped Markdown/JSON
discovery, standard-library SQLite job state and --mark/--history. Handled jobs
remain visible with truthful states and are excluded from the unhandled-job IDs.
Browser scripts are earlier
experiments; the CSV is a separate manual tracker.

Task 5 configures Muck Rack, LaunchDarkly, BaubleBar, Airtable, Figma, Reddit and
Rocket Lab as APPROVED/ACTIVE. SpaceX remains in the registry PAUSED with its original
identity/source. Cohort membership is a human + AI research/judgment decision,
explicitly approved by Adam; seven is intentional, not a Top-10 shortfall. No employer
score, replacement, speculative bench or rotation algorithm. Future cycles need
separate approval. Public mapping/approval metadata is recorded; unknown facts stay null.
28 focused foundation/configuration tests and all 112 tests passed. The bounded
live check succeeded for all seven sources (915 postings, 20 recognized roles before
location/state filtering). The operating guide records dated per-source evidence;
this is structural compatibility, not final usefulness or completeness acceptance.
Task 5 is committed at aab64a2eab60c7337a59e9e6ac6540aeb67a4be2; Adam reports the
push verified. Daily Close read-only checks found HEAD and local origin/main at
that hash with a clean starting tree; no new remote query was performed.

After that checkpoint, Adam reports a manual live run with the verified interpreter:
915 postings → 20 recognized → 18 displayed and unhandled under normal location
policy. Independent ChatGPT/Atlas research found substantially the same useful
population within the same seven employers. The operating guide preserves the
reported titles and ignored local evidence path. The possible Figma Senior Technical
Revenue Analyst difference was reviewed by Adam and is not a currently material
defect; no classifier expansion follows. These user-supplied observations were not
independently rerun during Daily Close.

This supports deterministic reduction/repeatability in the configured population,
not broader-market completeness, measured efficiency gains or commercial validation.
Greenhouse-only configuration excludes potentially excellent employers using other
career systems. The business consequence deserved earlier Product Owner challenge;
it is not a security defect or an implementation failure. The remaining value
question is whether repeatability/state/scale/control justify continued maintenance
over reasoning-AI-assisted discovery.

Task 4 adds explicit application records, append-only events, UNKNOWN/NO/YES
engagement, active employer suppression in selection_job_ids, reapply review after
unsuccessful engaged/unknown processes, job/context-specific overrides and explicit
review resolution. Complete discovery and sibling states remain truthful. Schema
v3 migration preserves old values and copies legacy application labels without
inventing applications/events; unresolved legacy history gates selection until
explicit reconciliation. The operating guide owns exact command semantics.
Task 4 tests use only temporary synthetic data; see BOOT_CONTEXT for final counts.
No real migration, live acceptance, external actions or release security clearance.

Task 3 recognizes primary title variants and senior/management adjacent families
as CLEAR MATCH or REVIEW NEEDED, with explicit reasons. Unknown geography remains
reviewable; clearly outside-area roles stay in history and are available through
--all-locations. --limit is retired with a visible error. Failed/unsearched ACTIVE
sources make source coverage incomplete. Task 4 adds separate selection suppression.
81 tests passed: 20 new discovery tests plus 61 retained/adapted regressions,
including all 27 registry/migration tests and four URL-security tests. Seven
zero-coverage fixture roles at one employer all appear. No live acceptance,
private database access/migration, dependencies or broad security scan in Task 3.

Task 2 adds employers.json and validation, canonical IDs and explicit source
mappings, ACTIVE/BENCH/PAUSED placement, schema v2, opt-in transactional legacy
migration, and per-source run observations. At that checkpoint four ACTIVE/PILOT
employers were configured, with no researched cohort or automatic rotation. Normal legacy commands
stop for explicit migration; private data was not accessed/migrated in this task.
Source observations distinguish failed fetches (null counts) from observed zero
yield. Historical job records remain when configuration removes an employer.
Historical Task 2 verification: 61 tests passed (34 existing regressions, 27 foundation tests),
including synthetic migration/rollback and simulated four-pilot integration.
No new live acceptance or broad security scan; real migration remains unauthorized.

At the September 25 checkpoint, 34 tests passed (22 original, eight persistence,
four URL-security). A standard Codex Security scan reported one low-severity
application-URL/Markdown injection issue; ingestion validation and output
revalidation/encoding were implemented with focused tests. This is targeted
remediation evidence, not a later full scan or clearance for the redesign.

Recorded isolated live acceptance: four feeds succeeded twice, 3,428 postings,
nine target roles; marking one job APPLIED changed five recommendations to four,
while all nine records and its APPLIED state remained. See the Job Scout README
for historical evidence location/limitations. This does not verify future employer
suppression, portfolio history or export.

## Approved milestones

- [x] Task 1: specifications and permanent close/recovery procedures; local checkpoint
  6ab7fac verified at Task 2 opening. Remote was not queried in Task 2.
- [x] Task 2: registry/canonical identity/pool/source-observation foundation and
  versioned schema with synthetic legacy migration/rollback tests. Local checkpoint
  364d49b verified at Task 3 opening; remote was not queried.
- [x] Task 5: configure the initial Product Owner-approved seven-employer cycle,
  preserving canonical identity and history; source mappings/live compatibility verified.
  Earlier Top-10 target superseded by explicit approval; future cohorts need new approval.
- [x] Task 3: broad accounting/finance discovery, review-needed eligibility,
  informational coverage and untruncated employer-grouped output; fixture verified.
  Local checkpoint 574d7e2 verified at Task 4 opening; remote was not queried.
- [x] Task 4: separate employer suppression, explicit opportunity override, legacy
  reconciliation and factual application/event history; synthetic acceptance verified.
  New actual applications create new records; prior closed records remain immutable.
  Local checkpoint 0159b0e verified at Task 5 opening; remote was not queried.
- [ ] Review minimal Job Scout closure/release disposition and remaining incremental
  value before deciding whether any additional work is warranted.
- [ ] Resolve applicable acceptance/security gates before any separately authorized
  Release Close; this documentation task does not perform Release Close.

Broader portfolio/manual opportunities, optional Excel export and multi-ATS support
remain unapproved for implementation. Previously specified portfolio/export criteria
below are deferred candidates, not an automatic build queue. Any substantial follow-on
must pass the Build-vs-Existing Capability Gate in OPERATING_SYSTEM. A Product Owner
scope disposition must explicitly retain/defer/remove criteria before release;
this close does not silently mark them satisfied or cancel them.

## Redesigned v1 acceptance gates — release remains open

- [x] Configure approved cycle-based Greenhouse cohort with explicit pool mechanics
  and visible source health: seven approved ACTIVE sources, SpaceX PAUSED. Task 5
  verifies configuration/compatibility; scoped comparison now exists, while final
  incremental-value and release disposition remain open.
- [ ] All broadly relevant opportunities surfaced; primary roles recognized;
  adjacent finance families/ambiguous geography shown REVIEW NEEDED; default junior
  exclusions and incompatible geography handled as specified. Empty live feeds
  are reported honestly, not padded or treated as proof of complete coverage.
  Task 3 verifies implemented deterministic rules on fixtures; Adam's live comparison
  now supports useful population coverage within the seven-employer scope, including
  displayed Assistant Controller roles. It is not exhaustive recall or broader-market
  proof; final scope/acceptance disposition remains open.
- [ ] LA/California-remote/hybrid policy verified; score is transparent
  accounting-signal coverage, not candidate-fit or hiring probability.
  Fixture cases pass in Task 3; live eligibility still requires human review.
- [ ] Final user acceptance of selection after run → explicitly record application
  → rerun, with truthful visible sibling states. Task 4 verifies this on synthetic
  fixtures, plus rejection/withdrawal/closure, unresolved offers, multiple applications,
  overrides and reapply review. Complete discovery remains intact. No accepted/
  declined/expired outcomes are inferred; CLOSED is an explicit ended relationship.
- [ ] Existing private SQLite records survive separately authorized migration.
  Synthetic preservation/rollback and explicit canonical identity are verified in
  Tasks 2/4; private backup/restoration planning and real migration remain outstanding.
- [ ] **Deferred candidate, not build authorization:** Portfolio persists factual fields, null unknowns, manual/recruiter opportunities
  and interview/outcome updates without fabricating applications or career evidence.
- [ ] **Deferred candidate, not build authorization:** Optional workbook has Open Opportunities, Application Portfolio and Employer
  Pool / Source Health views; SQLite stays authoritative; evidence/unknowns remain
  truthful; sensitive fields are omitted by default; artifacts are ignored and
  external text cannot become executable spreadsheet formulas.
- [ ] Final handoff/value disposition: Adam's comparison supports discovery usefulness
  in the approved population. Incremental maintenance value, tracking benefits and
  disposition of deferred export remain unresolved. No runtime application-writing
  acceptance is required.
- [ ] Relevant regressions pass, security disposition covers final changes,
  docs/recovery/workpapers match implementation, and authorized release checkpoint/
  tag and remote verification complete under Release Close.

## Superseded historical criteria

Earlier roadmap gaps were live Controller coverage and application-ready summary
acceptance. The historical live run demonstrated Senior Accountant/Accounting
Manager roles, not Controller listings. Primary Controller eligibility remains
part of the new discovery contract; absence of a current live posting is not
solved by inventing one. Verify rules with fixtures and live results with truthful
coverage/source-health reporting.

Algorithmic Top 5, runtime application-ready summaries, resume bullets and
recruiter messages are no longer release requirements. They were superseded by
product-owner approval, not retroactively verified. Task 3 replaced the normal
Top-5 output with complete discovery. Dated workpapers retain historical context.

## Next major phase — AI Controller Capability Benchmark planning

First review whether Job Scout needs minimal closure/release disposition before
shifting focus. Do not automatically implement Bank Recon, journal-entry automation
or another Controller module because it appeared on an older roadmap.

Plan a cheap comparison for a bounded candidate: bank reconciliation, journal-entry
drafting, variance analysis, balance-sheet reconciliation/close review or audit PBC
preparation. Compare A: reasoning AI/Atlas only; B: existing accounting/office tools
where relevant; C: the current/manual baseline where useful. Define a common case,
expected evidence, acceptable errors and success criteria before execution.

Evaluate setup effort, processing time, quality/accuracy, exception handling,
repeatability, evidence/auditability, compute/cost, human effort and privacy/control
requirements. Ask where reasoning AI actually struggles; build only for a demonstrated
meaningful gap under the operating system's integrated gate. A possible hybrid is
high-volume deterministic preprocessing → reasoning AI for exceptions/ambiguity →
human approval of consequential accounting judgments. This is a candidate pattern,
not an architecture selected in advance of evidence.

Tonight documents the direction only: no benchmark implementation, accounting
integration or sensitive-data access. Prefer synthetic cases; any later real-data
use requires SECURITY's activation review and explicit authorization.

Existing foundation: Git/GitHub and editor workflow, Python, earlier Playwright
experiments, security policy, recovery context and workpapers. Life Admin, LinkedIn
Assistant, Revenue Agent, Venture Lab, Finance Dashboard and a disaster-recovery
drill remain parked ideas, not authorized builds.
