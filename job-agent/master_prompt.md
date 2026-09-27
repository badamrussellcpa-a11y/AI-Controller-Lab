# Job Scout — approved product contract

**Approved direction, September 26, 2026. Not a claim of implemented functionality.**
Task 2 implements the registry, canonical identity, explicit pool placement,
schema/migration and observed-source foundation described below. Task 3 implements
broader deterministic discovery and employer-grouped output. Task 4 implements
explicit application lifecycle/history and employer selection restrictions.
Task 5 configures the approved seven-employer cycle; no cohort ranking algorithm.
Broader strategic portfolio/manual opportunities and export are deferred candidate
scope, not authorization to implement. September 26 post-checkpoint acceptance
informs a value/closure review before any additional features.
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

## Product Owner-approved cohort — Task 5

v1 remains Greenhouse-first. The initial production-oriented ACTIVE cohort is
intentionally seven: Muck Rack, LaunchDarkly, BaubleBar, Airtable, Figma, Reddit and
Rocket Lab. Adam completed human/AI research and approved this cycle. ACTIVE means
employers approved for the current application/search cycle, not a fixed Top-10
quota. Deterministic Scout does not select, score, rank or substitute employers.

The registry records approval and verified explicit source mappings. Rocket Lab,
Figma and Reddit retain their original canonical IDs. SpaceX retains its historical
identity/source as PAUSED; changing pool never deletes jobs/applications/history.
No speculative bench or automatic rotation is added. Unknown optional facts remain
null; only public, non-sensitive configuration rationale belongs in the repository.

Future cohorts require separate human/AI research and explicit Product Owner
approval. Application facts may inform that judgment without automatically changing
cohort membership. Source compatibility is verified separately from usefulness.
Adam's post-checkpoint comparison found substantially the same useful roles as
independent AI-assisted research within these seven employers; dated evidence and
limits are in [README.md](README.md).

## Source boundary and incremental value — September 26 reconciliation

The current architecture is Greenhouse-only and explicitly configured. Its business
consequence is exclusion of potentially excellent employers using other ATS/career
systems; it cannot represent the broader labor market. That consequence was not
sufficiently challenged before substantial implementation. This is a product/
architecture limitation, not a security defect or implementation failure.

Scout demonstrates deterministic reduction/repeatability plus implemented state,
history and controls. Whether these provide enough incremental value over reasoning-
AI-assisted discovery to justify maintenance remains open. The possible Figma
Senior Technical Revenue Analyst difference was reviewed by Adam and is not a
material current defect or reason to expand the classifier.

Apply the integrated Build-vs-Existing Capability Gate in OPERATING_SYSTEM before
substantial additional implementation. The portfolio/export descriptions below
preserve prior design intent if separately approved; they are not a next-task
instruction. Excel, broader portfolio and multi-ATS implementation remain unapproved.
Final minimal closure/release disposition requires Product Owner review.

## Discovery and eligibility — implemented in Task 3; scoped live evidence recorded

Surface **all** broadly relevant accounting/finance opportunities from the active
population. Task 3 removes Top-5 truncation and retires --limit with a clear error.
Output is grouped by canonical employer, then CLEAR MATCH before REVIEW NEEDED,
family order and stable title/ID. Neither coverage nor salary controls ordering.
Completeness is bounded by the documented deterministic rules and successfully
searched sources; failures or omitted ACTIVE sources are explicitly disclosed.

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

The complete discovery view includes handled jobs with their saved states plainly
shown. The inexpensive fresh_job_ids field lists only NEW/SHORTLISTED jobs within
the broad location policy; it means unhandled state, not verified actionability or
candidate fit. Absent jobs remain in history, not falsely presented as current.
Task 3 changes no database schema or migration behavior.

## Job state and separate employer relationship — Task 4 implemented

Existing job states remain NEW, SHORTLISTED, APPLIED, INTERVIEW, REJECTED, OFFER,
SKIP. Task 2 implements explicit canonical employer identity and source mappings;
it never automatically merges parents, subsidiaries or similar names.
Application records/events are authoritative for lifecycle facts; discovery labels
alone never create applications. Explicit commands record facts, never submit them.

Applying to Company A's Controller job leaves its Accounting Manager and Senior
Accountant jobs NEW. Separately suppress the employer from the normal selection
queue while an application is active, unless explicitly overridden. APPLIED, INTERVIEW and an
unresolved OFFER count as active. Rejection with explicitly confirmed NO meaningful
engagement releases the employer only when no other restriction remains. Recruiter/
HR screens and interviews record engagement independently of outcome. An unsuccessful
engaged process requires REVIEW BEFORE REAPPLYING; unknown engagement also requires
human review, never an assumption of no engagement. Review may be explicitly cleared
with a reason, preserving evidence. There is no cooling-off timer.

WITHDRAWN and CLOSED mean the user explicitly records that the relationship ended;
neither invents accepted/declined/expired outcomes. Closure after engagement requires
review. Multiple actual applications may be recorded truthfully; one closure cannot
clear another active application.

Overrides authorize one saved job and its current restriction context, with reason
and timestamp. They persist without a timer; new applications, closure/review facts
or changed opportunity content require new authorization. They never create
applications, change sibling states or erase history. Complete discovery remains
visible with warnings. selection_job_ids is the separate controlled selection view;
fresh_job_ids remains the Task 3 unhandled-state list and is not that queue.

Schema v3 adds explicit applications, append-only lifecycle events, preserved legacy
labels and human decisions. Migration from v1/v2 preserves all prior values and
creates no inferred applications, dates or engagement. Legacy APPLIED/INTERVIEW/
OFFER/REJECTED labels without sufficient history require explicit reconciliation;
ordinary --mark cannot bypass this gate. Unknown remains unknown. Current eligibility
or review can be explicitly decided, or an independently recorded application linked.
Application-backed jobs use lifecycle commands rather than --mark. See the operating
guide for commands and narrow semantics. Any future real-data
migration requires an approved private backup, restoration plan/test as appropriate,
and explicit Adam authorization. Ordinary commands do not auto-migrate legacy data.

## Factual application portfolio — deferred candidate scope

Persist company, role/title, application date/status, seniority, known
compensation/range, work arrangement, location/commute context, evidence-backed
industry/company type/stage, opportunity source, explicitly recorded fit/strength
and gap notes, optional resume reference, optional recruiter/contact, interview
activity/outcomes and useful notes. Unknown optional values are null, not invented.

Support manual/recruiter-inbound opportunities not discovered by Scout; recording
an opportunity must not fabricate an application. Separate private career/contact
material from default analysis exports. The portfolio is not implemented today.

## Optional Excel analysis export — deferred candidate scope

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
The prior proposed v1 goal included discovery/tracking/export and an evidence-backed
handoff to Adam + ChatGPT. Implemented discovery/tracking and scoped comparison are
now evidence for a value review, not automatic authorization for the remaining
export/portfolio scope. See the roadmap's open gates and deferred candidate criteria;
no criterion is silently passed or removed by this reconciliation.

No auto-apply, email/Gmail integration, LinkedIn automation, dashboard/UI, cloud
database, paid job-search API, broad ATS expansion or unrelated refactoring.
No v1 completion or release tag until actual implementation and acceptance.
