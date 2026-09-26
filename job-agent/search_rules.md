# Job Scout – Search Rules

The sections below describe CURRENT implemented settings. Scoring rows, reject
terms and the commute JSON are runtime inputs; documentation edits must preserve
their parsed values. Future policy at the end is not implemented by this file.

## Priority Order

1. Controller
2. Assistant Controller
3. Accounting Manager
4. Senior Accountant
5. Finance Manager (only if accounting leadership responsibilities)

## Scoring Guide

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
- Consumer lending
- Mortgage
- Loan officer
- Insurance sales
- Collections-heavy roles

## Commute Preferences

Confirmed September 25, 2026: driving from Hollywood Boulevard and North Vista
Street, Los Angeles; target at most 45 minutes each way. Keep longer commutes
available as stretch opportunities rather than rejecting the role outright.

Current behavior: the default shortlist shows up to five
matching roles, without padding if fewer are available. Only NEW and SHORTLISTED
application states qualify; APPLIED, INTERVIEW, REJECTED, OFFER and SKIP are
excluded before selecting five. Unhandled jobs may reappear, so fresh does not
guarantee five previously unseen jobs.

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

## Approved future direction — not implemented

The [product contract](master_prompt.md) and [roadmap](../ROADMAP.md) supersede
the old Top-5/application-writing acceptance requirements. Current code continues
to use the settings above until separately changed and tested.

Future discovery must surface all broadly relevant roles from the approved active
employer pool. Keep the five primary role families; surface potentially relevant
FP&A/finance leadership, treasury, tax, audit, payroll management and AP/AR
management as REVIEW NEEDED where appropriate. Junior/staff/clerk roles remain
excluded by default. This paragraph does not expand today's title recognizers.

Normally include LA-area, California-eligible remote and plausible hybrid roles;
retain ambiguous geography as REVIEW NEEDED. Clearly incompatible geography stays
outside the normal queue while history is preserved as appropriate. Today's
limited city/remote screen does not yet implement this policy.

Any retained score is informational Accounting-signal coverage, never hiring or
candidate-fit probability or a definitive best-job ranking. Future employer
suppression is separate from truthful job states; applying to one job does not
mark sibling jobs APPLIED. Portfolio and Excel requirements remain planned.
