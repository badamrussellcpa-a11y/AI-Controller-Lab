# Job Scout — first working live-feed pilot

Fetches public Greenhouse employer feeds, screens accounting titles, applies the
weights in `search_rules.md`, and writes a readable shortlist plus a JSON snapshot.
No paid API, cloud database, extra Python packages, or application submissions.

## Run from the AI-Controller-Lab terminal

If Python is already available in your VS Code terminal:

```powershell
python .\job-agent\job_scout.py
```

The agent's terminal did not find `python` on PATH. This exact local Python runtime
was verified during the build and can be used instead:

```powershell
& 'C:\Users\Adam\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\job-agent\job_scout.py
```

This fallback belongs to the desktop app and may move after an app update. A normal
Python 3.10+ installation is sufficient; no dependency installation is needed.

Open the newest `shortlist-*.md` in `job-agent/results/`. Each run creates a new
timestamped report. The accompanying JSON retains descriptions and evidence.
The existing `job_tracker.csv` is a separate manual tracker; its sample rows are
not inputs to this live search and are never overwritten.

## Options

- `--all-locations`: include target roles outside the initial location screen.
- `--boards rocketlab spacex`: choose public Greenhouse board tokens.
- `--limit 20`: override the default five-result shortlist to show at most 20 candidates.
- `--output PATH`: write snapshots to a different folder.

Default pilot coverage: Rocket Lab, SpaceX, Figma, and Reddit. These are starter
data sources, not endorsements of employers or a complete market search. A board
can legitimately have zero target roles. Source failures are visible in the report.
Exit codes: 0 = all feeds succeeded; 1 = all feeds failed; 2 = partial feed failure.

## How to read results

- Score = matched signal weights / total weights, rounded to 0–100. Repeated
  keywords do not add extra points. This measures evidence coverage only.
- Candidates with excluded-topic mentions follow unflagged candidates, scores
  rank next, and your role priority breaks ties. Commute checks do not affect
  selection or ranking. The broad LA/remote location screen still applies.
- Finance Manager needs both an accounting signal and a leadership signal.
- Excluded terms in titles reject a job. Mentions in descriptions flag manual
  review because a keyword alone cannot establish the role's actual focus.
- The initial location screen recognizes selected LA-area city names and explicit
  remote locations. Remote does not establish California eligibility. The LA city
  list is incomplete; use `--all-locations` to inspect omitted roles.
- Pay is quoted as source excerpts, not converted into assumed annual base pay.
  Unknown pay is not zero. Your salary preference is shown but does not yet filter
  or boost a result. Non-dollar compensation needs manual review.
- Keywords can occur in qualifications, negations, or company boilerplate. Read the
  evidence and listing. Scores are not probabilities or final suitability judgments.
- Resume focus prompts suggest topics only; they do not invent your experience.

## Verify changes

```powershell
python -m unittest discover -s .\job-agent -p "test_job_scout.py" -v
```

Substitute the verified interpreter path above if `python` is unavailable.
Tests cover false titles, weighted scoring, eligibility caveats, excluded-topic
review, duplicates, pay excerpts, out-of-area filtering, and feed failures.

## Next acceptance step

Adam reviews the shortlist for actual usefulness: title fit, pay, commute, employer
appeal, and major missing qualifications. Use that feedback to refine rules and
expand employer coverage before calling this a finished release.

`browser.py` and `browser_test.py` remain earlier browser experiments; they are not
needed for this version. The former heading-only scraper has been replaced.

Source contract: [Greenhouse Job Board API](https://docs.greenhouse.io/job-board.html).
Public GET endpoints need no authentication; `content=true` includes descriptions.

## Commute review

`search_rules.md` now contains the confirmed driving origin and 45-minute limit
each way. Reports include morning and return Google Maps links. These links do
not supply travel times to the program and need no mapping subscription. Open a
link, confirm the actual office, and check expected weekday arrival/departure
times. With a travel-time range, use the upper bound for conservative planning.

Daily goal: five relevant jobs to review and potentially apply to. Results are
capped at five by default, with fewer shown if fewer match. Commute links are
optional and there is no commute quota or commute-based sorting. New-vs-seen and
applied-job tracking are not implemented yet. Runs remain manual.

To retain a checked route, ask the assistant to record the estimates and office
address. The optional local `commute_reviews.json` is keyed by job ID from the
report's JSON snapshot. Its format is:

```json
{
  "exampleboard:123": {
    "origin": "Hollywood Blvd and N Vista St, Los Angeles, CA",
    "mode": "driving",
    "listing_location": "Exact location text from the job",
    "office_address": "Verified office address",
    "checked_on": "2026-09-25",
    "arrival_time": "Weekdays 9am",
    "leave_work_time": "Weekdays 5pm",
    "outbound_minutes": 40,
    "return_minutes": 45
  }
}
```

The example is illustrative, not a checked commute. No review file is created
until a route is actually checked. Reviews older than 30 days, from a different
origin or mode, or attached to a changed listing location require rechecking.
Saved estimates can indicate whether both directions meet the preference, but
they never lower a job's rank or prevent it appearing in the shortlist.
Even recorded route estimates are not guarantees. Reconfirm office attendance
and worksite details with the employer, especially for hybrid/multi-office roles.

Maps link reference: [Google Maps URLs](https://developers.google.com/maps/documentation/urls/get-started).
