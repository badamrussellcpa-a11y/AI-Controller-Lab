"""Read public Greenhouse listings without API keys or browser automation."""
import html
from html.parser import HTMLParser
import json
import re
import unicodedata
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def plain_text(value):
    parser = PlainText()
    parser.feed(html.unescape(html.unescape(value or "")))
    return " ".join(" ".join(parser.parts).split())


def validate_application_url(value):
    """Validate without rewriting source URLs or assuming a Greenhouse-only host."""
    error = "Source returned an invalid application URL"
    # Check before urlsplit, which otherwise silently strips some controls.
    if (not isinstance(value, str) or not value
            or any(c.isspace() or unicodedata.category(c).startswith("C") for c in value)
            or "\\" in value
            or re.search(r"%(?![0-9a-fA-F]{2})|%(?:0[0-9a-f]|1[0-9a-f]|7f)", value, re.I)):
        raise ValueError(error)
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        port = parsed.port  # Reject malformed or out-of-range ports.
        if (parsed.scheme not in {"http", "https"} or not host
                or parsed.username is not None or parsed.password is not None
                or parsed.netloc.endswith(":") or port == 0):
            raise ValueError(error)
        if ":" not in host:  # urlsplit already validates bracketed IPv6 addresses.
            dns_host = host.encode("idna").decode("ascii").rstrip(".")
            if len(dns_host) > 253 or not all(re.fullmatch(
                    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", label)
                    for label in dns_host.split(".")):
                raise ValueError(error)
    except (ValueError, UnicodeError):
        raise ValueError(error) from None
    return value


def fetch_jobs(board, company):
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", board):
        raise ValueError("Invalid board token")
    endpoint = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
    request = Request(endpoint, headers={"User-Agent": "JobScout/1.0"})
    with urlopen(request, timeout=25) as response:
        payload = json.load(response)
    if not isinstance(payload.get("jobs"), list):
        raise ValueError("Source did not return a jobs list")
    jobs = []
    for entry in payload["jobs"]:
        if not entry.get("id") or not entry.get("title") or not entry.get("absolute_url"):
            raise ValueError("Source returned an incomplete job record")
        jobs.append({
            "id": f"{board}:{entry['id']}", "company": company,
            "title": plain_text(entry["title"]),
            "location": plain_text((entry.get("location") or {}).get("name", "")),
            "description": plain_text(entry.get("content", "")),
            "url": validate_application_url(entry["absolute_url"]), "source": endpoint,
            "updated_at": entry.get("updated_at", ""),
        })
    return jobs
