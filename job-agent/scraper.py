"""Read public Greenhouse listings without API keys or browser automation."""
import html
from html.parser import HTMLParser
import json
import re
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
            "url": entry["absolute_url"], "source": endpoint,
            "updated_at": entry.get("updated_at", ""),
        })
    return jobs
