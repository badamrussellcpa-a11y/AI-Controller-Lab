# Job Scout – Search Rules

The sections below describe CURRENT implemented rules. Weighted coverage rows,
reject terms and commute JSON are runtime inputs. Task 3 keeps weights and commute
settings unchanged and adds explicit auto-lending/loan-origination title exclusions.
Full role/location patterns live in job_scout.py; this document explains the policy.

## Primary family display order

1. Controller
2. Assistant Controller
3. Accounting Manager
4. Senior Accountant
5. Finance Manager (REVIEW NEEDED; description scope checked independently of coverage)

## Accounting-signal coverage

Weighted share of the configured vocabulary found in a posting, rounded to 0–100.
Each signal counts once. Informational only: never inclusion, ordering, a result
limit, employer pool selection, candidate fit or hiring probability.

| Signal | Points |
|--------|-------:|
| Month-end close | +10 |
| General ledger ownership | +10 |
| Financial reporting | +9 |
| Balance sheet reconciliations | +9 |
| Journal entries | +8 |
| Audit support | +8 |
| Fixed assets | +7 |
| Intercompany | +7 |
| ERP systems | +6 |
| Team leadership | +5 |

## Automatic Reject

- Auto finance
- Auto lending
- Consumer lending
- Mortgage
- Loan officer
- Loan origination
- Insurance sales
- Collections-heavy roles

## Commute Preferences

Confirmed September 25, 2026: driving from Hollywood Boulevard and North Vista
Street, Los Angeles; target at most 45 minutes each way. Keep longer commutes
available as stretch opportunities rather than rejecting the role outright.

Current discovery is untruncated and includes handled jobs with their state shown.
Only NEW/SHORTLISTED within the broad location policy enter fresh_job_ids (unhandled,
not recommended). APPLIED/INTERVIEW/REJECTED/OFFER/SKIP remain visible in discovery
and history without that label. --limit is retired with an explicit CLI error.

Commute is an optional consideration, not a ranking factor or a quota. Review
routes only when useful; keep focus on job quality and applications.

```json
{
  "commute_origin": "Hollywood Blvd and N Vista St, Los Angeles, CA",
  "commute_mode": "driving",
  "commute_max_minutes": 45
}
```

The saved 45-minute preference is available for optional route checks. No travel
time is inferred from city names. Employer/location route links are starting
searches, not verified office addresses.

## Current role and geography policy — Task 3

The [product contract](master_prompt.md) and [roadmap](../ROADMAP.md) supersede
the old Top-5/application-writing requirements. Primary accounting title variants
are CLEAR MATCH (a role-family label, not suitability). Senior/management FP&A,
finance leadership, treasury, tax, audit, payroll and AP/AR are REVIEW NEEDED.
Credit/accounting operations and Finance Manager need description evidence of
accounting/finance scope; missing descriptions remain REVIEW NEEDED. Nonempty
descriptions without that scope do not qualify these ambiguous families.

Junior/staff/clerk/bookkeeper/intern roles and unrelated controller/technical/
sales/product-manager titles are excluded by default. The reject topics above
reject title matches; description mentions flag review rather than establishing
the actual role's focus. Exclusions also recognize Finance & Insurance titles.
Missing descriptions and other review flags downgrade a displayed role to
REVIEW NEEDED without using coverage as a gate.

Recognized LA-area and LA-hybrid labels are compatible, as are explicit California
remote or all-50-states/anywhere-in-US remote labels. Ordinary Remote/US, mixed
remote-region labels and unknown cities are REVIEW NEEDED — LOCATION, not dropped.
Explicit non-CA state/recognized outside-country labels and California exclusions
are incompatible with the normal view. They remain stored and --all-locations
shows them for inspection without treating them as fresh/actionable.
This is a conservative label parser, not geocoding or verified residency eligibility.
No commute time is inferred.

## Employer application controls — Task 4

Complete discovery and fresh_job_ids retain their Task 3 meanings. The separate
selection_job_ids list also requires an eligible employer relationship or a valid
job-specific override. Active applications and unresolved reapply review suppress
selection without changing sibling job states or hiding discovery. Legacy
application labels with unknown history require explicit reconciliation first.
Application facts, review/override decisions and evidence live in the private
SQLite lifecycle tables, not this rules file. See README for the lifecycle policy.

## Still planned

Researched final employer selection, broader strategic portfolio analytics,
manual opportunities, employer replacement and Excel export remain planned.
