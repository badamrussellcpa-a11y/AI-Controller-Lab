"""Explicit employer/source configuration. No identity inference or network access."""
from datetime import date
import json
from pathlib import Path
import re
import unicodedata

DEFAULT_REGISTRY = Path(__file__).resolve().parent / "employers.json"
POOLS = {"ACTIVE", "BENCH", "PAUSED"}
APPROVALS = {"PILOT", "APPROVED", "PENDING", "REJECTED"}
OPTIONAL = {"approval_date", "industry", "size_band", "company_stage_type",
            "la_evidence", "remote_evidence", "selection_rationale",
            "research_reference", "research_checked_date", "confidence_notes"}
REQUIRED = {"employer_id", "display_name", "greenhouse_boards", "approval_status", "pool"}


def _text(value):
    return (isinstance(value, str) and bool(value.strip()) and len(value) <= 4096
            and not any(unicodedata.category(c).startswith("C") for c in value))


def validate_registry(data):
    """Reject ambiguity/typos without echoing arbitrary configuration values."""
    if (not isinstance(data, dict) or set(data) != {"version", "employers"}
            or type(data["version"]) is not int or data["version"] != 1
            or not isinstance(data["employers"], list)):
        raise ValueError("Invalid employer registry format/version")
    ids, boards = set(), set()
    for entry in data["employers"]:
        if (not isinstance(entry, dict) or not REQUIRED <= set(entry)
                or set(entry) - REQUIRED - OPTIONAL):
            raise ValueError("Invalid employer registry fields")
        employer_id = entry["employer_id"]
        if (not isinstance(employer_id, str)
                or not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", employer_id)
                or len(employer_id) > 64 or employer_id in ids):
            raise ValueError("Invalid or duplicate canonical employer ID")
        ids.add(employer_id)
        if (not _text(entry["display_name"]) or not isinstance(entry["pool"], str)
                or entry["pool"] not in POOLS or not isinstance(entry["approval_status"], str)
                or entry["approval_status"] not in APPROVALS):
            raise ValueError("Invalid employer name, pool or approval status")
        if entry["approval_status"] in {"PENDING", "REJECTED"} and entry["pool"] != "PAUSED":
            raise ValueError("Unapproved employers must be PAUSED")
        mappings = entry["greenhouse_boards"]
        if not isinstance(mappings, list) or not mappings:
            raise ValueError("An employer requires explicit Greenhouse mappings")
        for board in mappings:
            if (not isinstance(board, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,100}", board)
                    or board.casefold() in boards):
                raise ValueError("Invalid or ambiguous Greenhouse source mapping")
            boards.add(board.casefold())
        for name in OPTIONAL & set(entry):
            value = entry[name]
            if value is not None:
                if not _text(value):
                    raise ValueError("Optional registry fields must be text or null")
                if name in {"approval_date", "research_checked_date"}:
                    try:
                        if date.fromisoformat(value).isoformat() != value:
                            raise ValueError()
                    except ValueError:
                        raise ValueError("Registry dates must be YYYY-MM-DD or null") from None
    return data


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key in employer registry")
        result[key] = value
    return result


def load_registry(path=DEFAULT_REGISTRY):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=_unique_keys)
    except json.JSONDecodeError:
        raise ValueError("Invalid employer registry JSON") from None
    return validate_registry(data)


def source_map(registry):
    validate_registry(registry)
    return {board: employer for employer in registry["employers"]
            for board in employer["greenhouse_boards"]}


def select_sources(registry, requested=None):
    mappings = source_map(registry)
    selected = list(dict.fromkeys(requested)) if requested is not None else [
        board for board, employer in mappings.items() if employer["pool"] == "ACTIVE"]
    if any(board not in mappings or mappings[board]["pool"] != "ACTIVE"
           or mappings[board]["approval_status"] not in {"PILOT", "APPROVED"}
           for board in selected):
        raise ValueError("Requested board requires an explicit ACTIVE PILOT/APPROVED registry mapping")
    return {board: mappings[board] for board in selected}
