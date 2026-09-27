"""Explicit local application facts and derived employer controls; no external actions."""
from contextlib import closing
from datetime import date, datetime, timezone
import json
from pathlib import Path
import unicodedata

from application_state import connect

ACTIVE = {"APPLIED", "SCREEN", "INTERVIEW", "OFFER"}
CLOSED = {"REJECTED", "WITHDRAWN", "CLOSED"}
EVENTS = ACTIVE | CLOSED


def _now():
    return datetime.now(timezone.utc).isoformat()


def _text(value, required=False):
    if value is None and not required:
        return None
    if (not isinstance(value, str) or not value.strip() or len(value) > 2000
            or any(unicodedata.category(c).startswith("C") and c not in "\n\r\t" for c in value)):
        raise ValueError("A nonblank reason of at most 2000 characters without control codes is required")
    return value.strip()


def _when(value):
    if value is None:
        return None  # Recording time is never substituted for a historical fact.
    try:
        if len(value) == 10 and date.fromisoformat(value).isoformat() == value:
            return value
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is not None:
            return parsed.isoformat()
    except (ValueError, TypeError):
        pass
    raise ValueError("Use YYYY-MM-DD or an ISO timestamp with timezone; omit unknown dates")


def _open(path):
    if not Path(path).is_file():
        raise ValueError("No saved state; discover jobs first using an authorized state file")
    return connect(path)


def _rows(connection, sql, values=()):
    cursor = connection.execute(sql, values)
    names = [column[0] for column in cursor.description]
    return [dict(zip(names, row)) for row in cursor]


def _audit(connection):
    applications = _rows(connection, "SELECT * FROM applications ORDER BY application_id")
    events = _rows(connection, "SELECT * FROM application_events ORDER BY event_id")
    for app in applications:
        app["events"] = [e for e in events if e["application_id"] == app["application_id"]]
        if not app["events"] or app["events"][0]["event"] != "APPLIED":
            raise ValueError("Incomplete application event history; stopped")
        app["stage"] = app["events"][-1]["event"]
        values = [e["engagement"] for e in app["events"]]
        # YES is historical evidence forever. A previous NO cannot establish
        # that no interaction occurred between that observation and closure.
        app["engagement"] = "YES" if "YES" in values else values[-1]
    return {"applications": applications,
            "legacy_facts": _rows(connection, """SELECT f.*, j.employer_id FROM legacy_application_facts f
                JOIN jobs j ON j.id=f.job_id ORDER BY fact_id"""),
            "decisions": _rows(connection, "SELECT * FROM employer_decisions ORDER BY decision_id")}


def read_applications(path):
    with closing(_open(path)) as connection:
        connection.execute("BEGIN")
        audit = _audit(connection)
        for decision in audit["decisions"]:
            decision["context_evidence"] = json.loads(decision["context"])
        return audit


def _context(tokens):
    return json.dumps(sorted(tokens), separators=(",", ":"))


def _opportunity_context(restriction_context, snapshot):
    job = json.loads(snapshot)
    # Stable listing identity/content, not fetched timestamps, coverage or pay parsing.
    content = {k: job.get(k) for k in ("id", "title", "location", "description", "url")}
    return json.dumps({"restriction_facts": json.loads(restriction_context), "opportunity": content},
                      ensure_ascii=True, sort_keys=True)


def _relationships(connection):
    audit = _audit(connection)
    jobs = dict(connection.execute("SELECT id, job_json FROM jobs"))
    relationships = {}
    for (employer_id,) in connection.execute("SELECT employer_id FROM employers ORDER BY employer_id"):
        apps = [a for a in audit["applications"] if a["employer_id"] == employer_id]
        decisions = [d for d in audit["decisions"] if d["employer_id"] == employer_id]
        restrictions, review = [], []
        for app in apps:
            app_id = app["application_id"]
            if app["stage"] in ACTIVE:
                restrictions.append({"token": f"active:{app_id}", "kind": "ACTIVE APPLICATION",
                    "reason": f"Application {app_id}: {app['title']}; {app['stage']}; submitted {app['submitted_at'] or 'UNKNOWN'}"})
            elif app["engagement"] != "NO":
                review.append({"token": f"closed:{app_id}:{app['events'][-1]['event_id']}",
                    "kind": "REVIEW BEFORE REAPPLYING",
                    "reason": f"Application {app_id}: {app['title']}; {app['stage']}; meaningful engagement {app['engagement']}"})
        # A legacy label cannot be erased by changing the current discovery label.
        for fact in audit["legacy_facts"]:
            if fact["employer_id"] != employer_id:
                continue
            token = f"legacy:{fact['fact_id']}"
            resolved = [d for d in decisions if d["action"].startswith("LEGACY_")
                        and token in json.loads(d["context"])]
            if not resolved:
                restrictions.append({"token": token, "kind": "RECONCILIATION REQUIRED",
                    "reason": f"Legacy job {fact['job_id']}: {fact['status']}; application/engagement history UNKNOWN"})
            elif resolved[-1]["action"] == "LEGACY_REVIEW":
                review.append({"token": f"legacy-review:{resolved[-1]['decision_id']}",
                    "kind": "REVIEW BEFORE REAPPLYING", "reason": resolved[-1]["reason"]})
        cleared = {token for d in decisions if d["action"] == "REVIEW_CLEARED"
                   for token in json.loads(d["context"])}
        restrictions += [r for r in review if r["token"] not in cleared]
        kinds = {r["kind"] for r in restrictions}
        status = next((kind for kind in ("RECONCILIATION REQUIRED", "ACTIVE APPLICATION", "REVIEW BEFORE REAPPLYING")
                       if kind in kinds), "ELIGIBLE")
        # New applications or closure facts invalidate older authorizations, even
        # when another active application leaves the visible label unchanged.
        revisions = [f"event:{e['event_id']}" for a in apps for e in a["events"]
                     if e["event"] == "APPLIED" or e["event"] in CLOSED]
        revisions += [f"decision:{d['decision_id']}" for d in decisions if d["action"] != "OVERRIDE"]
        context = _context([r["token"] for r in restrictions] + revisions)
        overrides = [d for d in decisions if d["action"] == "OVERRIDE"
                     and d["context"] == _opportunity_context(context, jobs[d["job_id"]])]
        relationships[employer_id] = {"status": status, "restrictions": restrictions,
            "context": context, "overrides": overrides, "applications": apps,
            "reason": "; ".join(r["reason"] for r in restrictions) or "No unresolved application restriction"}
    return relationships


def employer_relationships(path):
    with closing(_open(path)) as connection:
        connection.execute("BEGIN")
        return _relationships(connection)


def consideration(relationship, job_id):
    if relationship["status"] == "RECONCILIATION REQUIRED":
        return False, "RECONCILIATION REQUIRED — " + relationship["reason"]
    override = next((d for d in reversed(relationship["overrides"]) if d["job_id"] == job_id), None)
    if override and relationship["restrictions"]:
        return True, f"OVERRIDE ACTIVE — {override['reason']} (recorded {override['recorded_at']}; decision {override['decision_id']})"
    if relationship["status"] == "ACTIVE APPLICATION":
        return False, "ACTIVE APPLICATION AT THIS EMPLOYER — REVIEW BEFORE SECOND APPLICATION"
    return relationship["status"] == "ELIGIBLE", relationship["status"] + " — " + relationship["reason"]


def record_application(path, job_id, submitted_at=None):
    submitted_at = _when(submitted_at)
    with closing(_open(path)) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute("SELECT employer_id, job_json FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not row:
            raise ValueError("Unknown saved job ID")
        audit = _audit(connection)
        if any(a["job_id"] == job_id and a["stage"] in ACTIVE for a in audit["applications"]):
            raise ValueError("This job already has an active application; record an event instead")
        # Recording a factual application must remain possible even if it violated
        # selection policy. This command records a user fact; it never submits.
        now = _now()
        app_id = connection.execute("""INSERT INTO applications
            (employer_id, job_id, title, submitted_at, recorded_at, provenance)
            VALUES (?, ?, ?, ?, ?, 'EXPLICIT_USER')""",
            (row[0], job_id, json.loads(row[1])["title"], submitted_at, now)).lastrowid
        connection.execute("""INSERT INTO application_events
            (application_id, event, engagement, occurred_at, recorded_at, reason)
            VALUES (?, 'APPLIED', 'UNKNOWN', ?, ?, NULL)""", (app_id, submitted_at, now))
        connection.execute("UPDATE jobs SET status='APPLIED', status_updated_at=? WHERE id=?", (now, job_id))
        return app_id


def record_event(path, application_id, event, engagement="UNKNOWN", occurred_at=None, reason=None):
    if event not in EVENTS - {"APPLIED"} or engagement not in {"UNKNOWN", "NO", "YES"}:
        raise ValueError("Invalid application event or engagement value")
    reason, occurred_at = _text(reason, event in CLOSED), _when(occurred_at)
    if event in {"SCREEN", "INTERVIEW"}:
        if engagement == "NO":
            raise ValueError("A screen/interview records meaningful engagement")
        engagement = "YES"
    with closing(_open(path)) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        app = next((a for a in _audit(connection)["applications"] if a["application_id"] == application_id), None)
        if not app:
            raise ValueError("Unknown application ID")
        if app["stage"] in CLOSED:
            raise ValueError("Application is closed; history is immutable. Record a new actual application separately")
        if app["engagement"] == "YES" and engagement == "NO":
            raise ValueError("Cannot erase previously recorded meaningful engagement")
        if app["stage"] == "OFFER" and event not in CLOSED:
            raise ValueError("Offer remains active until explicit closure; cannot silently downgrade it")
        now = _now()
        connection.execute("""INSERT INTO application_events
            (application_id, event, engagement, occurred_at, recorded_at, reason)
            VALUES (?, ?, ?, ?, ?, ?)""", (application_id, event, engagement, occurred_at, now, reason))
        status = {"SCREEN": "INTERVIEW", "WITHDRAWN": "SKIP", "CLOSED": "SKIP"}.get(event, event)
        connection.execute("UPDATE jobs SET status=?, status_updated_at=? WHERE id=?", (status, now, app["job_id"]))


def decide(path, employer_id, action, reason, job_id=None, application_id=None):
    reason = _text(reason, True)
    if action not in {"OVERRIDE", "REVIEW_CLEARED", "LEGACY_ELIGIBLE", "LEGACY_REVIEW", "LEGACY_LINKED"}:
        raise ValueError("Invalid employer decision")
    with closing(_open(path)) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        relation = _relationships(connection).get(employer_id)
        if not relation:
            raise ValueError("Unknown canonical employer ID")
        if job_id is not None:
            row = connection.execute("SELECT employer_id FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not row or row[0] != employer_id:
                raise ValueError("Job does not belong to the specified canonical employer")
        if action == "OVERRIDE":
            if job_id is None or not relation["restrictions"] or relation["status"] == "RECONCILIATION REQUIRED":
                raise ValueError("Override requires a specific job and a known current restriction; reconcile legacy facts first")
            status, snapshot = connection.execute("SELECT status, job_json FROM jobs WHERE id=?", (job_id,)).fetchone()
            if status not in {"NEW", "SHORTLISTED"}:
                raise ValueError("Opportunity authorization requires an unhandled sibling job")
            context = _opportunity_context(relation["context"], snapshot)
        elif action == "REVIEW_CLEARED":
            tokens = [r["token"] for r in relation["restrictions"] if r["kind"] == "REVIEW BEFORE REAPPLYING"]
            if not tokens or job_id is not None:
                raise ValueError("No unresolved employer reapply review to clear")
            context = _context(tokens)
        else:
            facts = [f for f in _audit(connection)["legacy_facts"] if f["job_id"] == job_id]
            if not facts:
                raise ValueError("A saved legacy job requiring reconciliation is necessary")
            context = _context([f"legacy:{f['fact_id']}" for f in facts])
            if action == "LEGACY_LINKED":
                app = connection.execute("SELECT job_id FROM applications WHERE application_id=?", (application_id,)).fetchone()
                if not app or app[0] != job_id:
                    raise ValueError("Reconciliation requires an explicit application for this same job")
        if action != "LEGACY_LINKED" and application_id is not None:
            raise ValueError("Application ID is only valid for linked legacy reconciliation")
        decision_id = connection.execute("""INSERT INTO employer_decisions
            (employer_id, job_id, application_id, action, context, reason, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (employer_id, job_id, application_id, action, context, reason, _now())).lastrowid
        return decision_id
