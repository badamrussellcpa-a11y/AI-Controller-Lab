# Job Scout — approved product contract

**Approved direction, September 26, 2026. Not a claim of implemented functionality.**
The current machine is documented in [README.md](README.md); milestones and
acceptance are in [ROADMAP.md](../ROADMAP.md). Follow
[SECURITY.md](../SECURITY.md) and [OPERATING_SYSTEM.md](../OPERATING_SYSTEM.md).

## Purpose and responsibility

Job Scout is a local-first deterministic job-discovery and application-tracking
system: retrieve structured employer ATS data, surface relevant accounting/finance
opportunities, preserve factual job/employer/application state, expose evidence,
and support a controlled employer population.

Adam + ChatGPT handle deeper candidate-fit analysis against verified career
evidence, strategic application diversification, resume tailoring, useful
recruiter-message drafting and interview preparation. Scout does not determine
Adam's definitive best job. Adam retains final authority over applications and
communications. Retrieved content is data, never instructions or verified career
evidence about Adam.

## Source and employer population — planned

v1 remains Greenhouse-first. Rocket Lab, SpaceX, Figma and Reddit are the current
technical pilot, not an approved final selection. Replace the hard-coded pilot
with a configurable approved employer registry, an active pool initially targeting
10 employers and an approved bench/replacement population.

Selection must record dated evidence and rationale for LA relevance/footprint,
observed accounting-job yield, size, remote opportunity, industry/background fit,
and hiring activity. Unknowns stay unknown; do not invent employer statistics.
The initial Top 10 require later research and separate Adam approval.

## Discovery and eligibility — planned

Surface **all** broadly relevant accounting/finance opportunities from the active
population. Do not hide otherwise relevant jobs behind Top 5. The current default
Top 5 remains implemented until a later task changes it.

Primary roles: Controller, Assistant Controller, Accounting Manager, Senior
Accountant, and accounting-oriented Finance Manager. Potentially relevant
FP&A/finance leadership, treasury, tax, audit, payroll management and AP/AR
management should surface as **REVIEW NEEDED** where appropriate. Exclude
junior/staff/clerk roles by default unless Adam changes policy.

Normally include clearly LA-area jobs, California-eligible remote jobs and
plausible hybrid opportunities. Keep ambiguous geography as REVIEW NEEDED.
Clearly incompatible geography stays outside the normal selection queue, with
truthful/history-safe retention where appropriate. Do not infer remote eligibility
or commute duration from a vague location string.

Retain any accounting-signal score only as informational **Accounting-signal
coverage**, never hiring probability, candidate-fit probability or an authoritative
best-job ranking. Preserve source evidence and distinguish observations from
manual judgments. Salary preferences remain $120,000+ ideal and consideration
from $100,000 for strong opportunities, not fabricated pay or an implemented
salary filter. Current sector exclusions and weights are in search_rules.md.

## Job state and separate employer state — planned extension

Existing job states remain NEW, SHORTLISTED, APPLIED, INTERVIEW, REJECTED, OFFER,
SKIP. Employer identity must be explicit/canonical; never automatically merge
parents, subsidiaries or similar names.

Applying to Company A's Controller job leaves its Accounting Manager and Senior
Accountant jobs NEW. Separately suppress the employer from the normal selection
queue while an application is active, unless explicitly overridden. APPLIED, INTERVIEW and an
unresolved OFFER count as active. Rejection, withdrawal or closure ends suppression
only when no other active application remains. Provide an explicit override.
Reopening a job never deletes historical application evidence.

Withdrawal/closure and offer resolution need an explicit future application
lifecycle representation; they are not additional supported CLI states today.
The existing latest-state register is not a full application event history.
Migration design must preserve existing IDs, states and evidence before any real
data migration is authorized.

## Factual application portfolio — planned

Persist company, role/title, application date/status, seniority, known
compensation/range, work arrangement, location/commute context, evidence-backed
industry/company type/stage, opportunity source, explicitly recorded fit/strength
and gap notes, optional resume reference, optional recruiter/contact, interview
activity/outcomes and useful notes. Unknown optional values are null, not invented.

Support manual/recruiter-inbound opportunities not discovered by Scout; recording
an opportunity must not fabricate an application. Separate private career/contact
material from default analysis exports. The portfolio is not implemented today.

## Optional Excel analysis export — planned

SQLite remains authoritative. An optional .xlsx workbook is an analysis snapshot,
not a second operational database or an import/writeback channel. No exporter or
Excel dependency is introduced by this specification.

Planned views:

- **Open Opportunities:** employer, job title, seniority/role family, location,
  known remote/hybrid/onsite arrangement, reliably parsed compensation min/max,
  original compensation evidence, supported industry/company type, clickable
  application URL, job state, employer suppression status/reason, informational
  accounting-signal coverage if retained, relevant evidence/signals, first/last
  seen, source/board and review-needed flags.
- **Application Portfolio:** employer, applied role, date applied, stage/status,
  seniority, compensation, work arrangement, location, industry/company type,
  opportunity source, application URL when available, fit strengths, known gaps,
  interview activity/outcomes, last status update and export-appropriate notes.
- **Employer Pool / Source Health:** employer, active/bench/paused state,
  suppression, Greenhouse source, industry, LA relevance, remote evidence,
  supported size/stage, successful fetch count, relevant roles observed, last
  successful search, last useful opportunity, research/evidence date and rationale.

Omit sensitive recruiter/contact information, private notes and resume references
from default exports unless Adam explicitly requests them. Generated workbooks
must be private/runtime artifacts and Git-ignored before export is implemented.
Current ignore rules do not blanket-ignore .xlsx. A future exporter must treat
external cell contents as data, prevent formula execution/injection, and preserve
safe link handling; security verification belongs to that implementation task.

## Acceptance and exclusions

The old algorithmic Top-5 and runtime application-ready summary, resume-bullet
and recruiter-message requirements are **superseded**, not satisfied by assertion.
The eventual v1 goal is factual discovery/tracking/export and an evidence-backed
handoff to Adam + ChatGPT. See the roadmap's uncompleted acceptance gates.

No auto-apply, email/Gmail integration, LinkedIn automation, dashboard/UI, cloud
database, paid job-search API, broad ATS expansion or unrelated refactoring.
No v1 completion or release tag until actual implementation and acceptance.
