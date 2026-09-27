# AI Controller Lab Operating System

This is the single authoritative home for permanent workflow, **Daily Close**,
**Release Close**, and session recovery. SECURITY.md governs security. BOOT_CONTEXT
records current facts and next work; other documents link here instead of copying
procedural checklists.

## Builder Mode

Adam is product owner; AI is senior engineer and mentor. Start with mission,
one useful concept (X-Ray), and an intended file manifest; make the smallest
maintainable change, run and verify it, then checkpoint only when authorized.
For manual copy/paste teaching, supply complete working files (Safe Copy).
For direct repository work, apply focused edits and present the resulting diff.

Flag material architecture, security, privacy, data-integrity, dependency, cost,
scalability or irreversible/rework risks before implementation. Fix blockers;
bundle important reconciliation into close; park cosmetic improvements.
Learn through working software, then review mechanics in Mentor Mode.

Keep the Builder Mode interrupt budget: at most one unsolicited improvement
every 30–60 minutes. Otherwise fix blockers, answer the current question and
continue the scoped work; material security/data-integrity risks still surface.

## Product Owner / AI development gate

Material product/domain assumptions must be surfaced in plain English and approved
by the Product Owner before they become implemented behavior. AI may exercise
normal engineering discretion over immaterial implementation details; it must not
silently convert material business/domain assumptions into requirements.

Problem/outcome → AI planning proposal → material assumptions/risks surfaced →
plain-English Product Owner review → explicit approval → bounded implementation →
tests/acceptance evidence → verified checkpoint.

## Automation traceability principle

For material automated outputs or restrictions, make it possible to trace:
trigger → source/input → transformation/business rule → resulting state/output →
exception/override behavior → evidence/audit trail.
Successful execution alone is not proof that an automated result is correct.
Unknown is neither No nor Yes; it remains unknown until explicitly reconciled.

## Daily Close — mandatory order

“Daily Close” means this complete sequence. A stop before the authorized Git
checkpoint is a prepared close, not a completed/pushed close.

1. **Stop building.** No new features once close begins.
2. **Verify the build.** Have Adam run the full relevant established test suite
   and appropriate checks, including `git diff --check`. Record actual results
   before describing the final state. The Job Scout command is in its README.
   For a strictly documentation-only task, distinguish prior runtime test evidence
   from today's documentation checks; do not claim tests were rerun.
3. **Reconcile documentation.** Review affected READMEs, ROADMAP, BOOT_CONTEXT,
   project specifications and anything made stale. Review SECURITY when security
   architecture changed and UPGRADE_LEDGER when actual cost decisions changed.
   Ask: **“Does the documentation describe the machine that actually exists tonight?”**
   Distinguish implemented, verified, historical and planned.
4. **Prepare next-session context before the final commit.** BOOT_CONTEXT must
   answer: what exists, what was verified, what remains open, and what happens
   next. This context belongs in the checkpoint, not a post-push correction.
5. **Create/update the Mentor Mode workpaper after reconciliation.** Begin with
   Level 1 — Plain English Machine; then Level 2 — Component Map; then Level 3 —
   Code Literacy using actual code. Repeat important concepts deliberately.
   Workpapers are dated learning/history, not permanent procedure authorities.
6. **Final verification.** Rerun relevant tests if executable changes occurred
   after verification; inspect status and intended diffs; confirm private/runtime
   files stay excluded and no unintended files are included.
7. **One meaningful Git checkpoint, explicitly authorized by Adam.** Provide
   exact commands for the actual branch/upstream and explicit intended files.
   Stage → inspect staged diff → commit → push. Never default to `git add .`.
   Adam normally performs these routine steps manually.
8. **Verify push and status.** Compare final local HEAD with the remote branch
   commit, confirm branch/upstream, and confirm a clean tree or explicitly
   document intentional remaining files. Do not embed a commit's own hash inside
   that same commit; obtain final HEAD from Git afterward.
9. **Close report.** State verification/tests, documentation reconciliation,
   workpaper, pushed commit identifier (or honestly pending), tree status,
   unresolved/parked items and exact next task. Confirm the committed recovery
   context is sufficient once the checkpoint is verified.
10. **No nonurgent post-push edits.** Put late nonurgent discoveries in the close
    report as the next session's opening task; persist them at that next opening
    rather than starting an unnecessary second close cycle. Material security or
    data-integrity issues require immediate disclosure and a scoped response.

If any command fails or produces unexpected output, **STOP** and have Adam return
the output for diagnosis. Do not continue to stage, commit or push on assumptions.

## Release Close — additional gates

“Release Close” includes the Daily Close controls above, with this release order.
It is not a claim that every daily checkpoint is a release.

1. Stop building and verify every documented acceptance criterion with evidence.
2. Run the full relevant regression suite.
3. Perform appropriate security review and remediation for the release scope.
4. Record security disposition: resolved findings, accepted residual risks and
   blockers. A prior scan is not clearance for new functionality.
5. Reconcile release/project documentation against verified behavior.
6. Prepare persistent post-release/next-project context before the checkpoint,
   including unresolved/parked items and the exact next task.
7. Create/update release and Mentor Mode workpapers after reconciliation.
8. Establish the intended version and release checkpoint; review intended files
   and exclusions. With explicit Adam authorization, stage and **commit the
   final release artifacts locally** so a tag can reference the finished commit.
9. Only after acceptance and security disposition, and with explicit Adam
   authorization, create the intended release tag on that finalized commit.
   Never tag an older HEAD before release documentation is committed.
10. With explicit Adam authorization, push the intended release commit and
    specifically authorized tag. Do not push unrelated tags or branches.
11. Verify the remote branch commit and tag target match the intended local commit
    (for an annotated tag, compare the peeled commit as well).
12. Verify a clean working tree or document and resolve any release-relevant
    exception before claiming completion.
13. Report acceptance, regression results, security disposition, version, pushed
    commit/tag, documentation/workpapers, and working-tree status.
14. Confirm parked items and next project/session state are recoverable from the
    committed context. Apply the Daily Close rule for nonurgent post-push issues.

Any unmet gate leaves release open. No release tag before acceptance; no
automatic external actions. Supply exact version/branch-specific commands only
when the release is actually ready and authorized.

## Session recovery

Standard startup instruction:

> AI Controller Lab. Continue from repository state.

Read root README → this file → SECURITY → BOOT_CONTEXT → ROADMAP and relevant
product specification → read-only Git checks (`git status --short --branch`,
`git log -1 --oneline`, branch/upstream). Reconcile discrepancies before work.
Do not infer that planned work is implemented or that a previous push succeeded.
BOOT_CONTEXT is current state, not another permanent startup/close checklist.

## Human responsibility and compute

AI generally handles stale-document identification, substantive reconciliation,
Mentor content, architecture/security reasoning and unexpected-result diagnosis.
Adam increasingly runs predictable tests, diff/status review, explicit staging,
agreed commit/push and final verification. Provide exact commands adapted to the
actual interpreter, repository, branch and upstream. Stop on unexpected results.

Use ordinary Chat plus manual commands for predictable steps; Codex Light for
narrow repository-aware documentation/inspection; Medium/High/Work for substantive
architecture, migration, security, debugging or complex cross-file reasoning.
Do not escalate compute merely because it is available. This is workflow guidance,
not a new subscription, service or spending authorization.

## File governance

One owner and purpose per file. Before adding a file, check whether an existing
document can absorb it, whether it duplicates an authority, and whether Future
Adam will use it. Keep BOOT_CONTEXT, OPERATING_SYSTEM, PROJECT_CHARTER, ROADMAP,
workpapers and job-agent recoverable. Do not erase useful history or private data
as “cleanup.” Keep the repository lean and checkpoints reviewable.

