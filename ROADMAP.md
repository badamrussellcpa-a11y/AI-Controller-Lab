# AI Controller Lab Roadmap

**Job Scout v1: in progress; Task 2 foundation implemented, broader redesign planned.**
The [product contract](job-agent/master_prompt.md) owns detailed requirements.
[OPERATING_SYSTEM.md](OPERATING_SYSTEM.md) owns Daily Close and Release Close.

## Current baseline and evidence

Implemented: four public Greenhouse pilot feeds, deterministic screening and
weighted evidence, default Top 5 Markdown/JSON reports, standard-library SQLite
job state, --mark/--history and handled-job exclusion. Browser scripts are earlier
experiments; the CSV is a separate manual tracker.

Task 2 adds employers.json and validation, canonical IDs and explicit source
mappings, ACTIVE/BENCH/PAUSED placement, schema v2, opt-in transactional legacy
migration, and per-source run observations. Four ACTIVE/PILOT employers remain;
no researched final population or automatic rotation. Normal legacy commands
stop for explicit migration; private data was not accessed/migrated in this task.
Source observations distinguish failed fetches (null counts) from observed zero
yield. Historical job records remain when configuration removes an employer.
Task 2 verification: 61 tests passed (34 existing regressions, 27 foundation tests),
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
  versioned schema with synthetic legacy migration/rollback tests. Manual Git
  checkpoint pending; verify subsequent commit/push from Git.
- [ ] Research and obtain Adam's approval for initial active target of 10 employers
  and bench; capture dated evidence, unknowns and selection rationale.
- [ ] Implement broad accounting/finance discovery, REVIEW NEEDED eligibility and
  informational scoring without hiding relevant jobs behind Top 5.
- [ ] Implement separate employer suppression, explicit override and factual
  application history that survives rejection, closure and reopening.
- [ ] Implement nullable application portfolio and manual/recruiter opportunities.
- [ ] Implement private optional .xlsx analysis export with three approved views.
- [ ] Verify redesigned acceptance and complete authorized Release Close.

Task sequence may be refined at each authorized design review without expanding
the product contract. Registry, schema, lifecycle and export changes must be
tested before touching real history.

## Redesigned v1 acceptance gates — release remains open

- [ ] Approved configurable Greenhouse employer population, active target 10 and
  bench/paused operation; evidence-backed selection and visible source health.
- [ ] All broadly relevant opportunities surfaced; primary roles recognized;
  adjacent finance families/ambiguous geography shown REVIEW NEEDED; default junior
  exclusions and incompatible geography handled as specified. Empty live feeds
  are reported honestly, not padded or treated as proof of complete coverage.
- [ ] LA/California-remote/hybrid policy verified; score is transparent
  accounting-signal coverage, not candidate-fit or hiring probability.
- [ ] End-to-end run → mark application → rerun excludes the handled job and
  suppresses its canonical employer while sibling job states remain truthful.
  Rejection/withdrawal/closure, unresolved/resolved offers, multiple applications,
  explicit override and reopening preserve history and correct suppression.
- [ ] Existing private SQLite records survive separately authorized migration.
  Synthetic preservation/rollback and explicit canonical identity are verified in
  Task 2; private backup/restoration planning and real migration remain outstanding.
- [ ] Portfolio persists factual fields, null unknowns, manual/recruiter opportunities
  and interview/outcome updates without fabricating applications or career evidence.
- [ ] Optional workbook has Open Opportunities, Application Portfolio and Employer
  Pool / Source Health views; SQLite stays authoritative; evidence/unknowns remain
  truthful; sensitive fields are omitted by default; artifacts are ignored and
  external text cannot become executable spreadsheet formulas.
- [ ] Adam reviews the factual discovery/tracking/export handoff as useful for
  deeper analysis with ChatGPT. No runtime application-writing acceptance required.
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
product-owner approval, not retroactively verified. Current Top 5 code persists
until replaced. Dated workpapers retain historical context.

## Foundation and future projects

Existing foundation: Git/GitHub and editor workflow, Python, earlier Playwright
experiments, security policy, recovery context and workpapers.

Controller Copilot (close, reconciliation, journal drafts, variance analysis,
audit workpapers) and Life Admin remain future projects. Parking lot: LinkedIn
Assistant, Revenue Agent, Venture Lab, Finance Dashboard, disaster-recovery drill.
These entries authorize no integration or sensitive-data access.
