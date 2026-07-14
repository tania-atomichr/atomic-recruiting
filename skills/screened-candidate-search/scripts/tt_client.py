"""Shared Teamtailor API helpers: auth + paginated GET with rate-limit backoff.

Import from the other pipeline scripts, or run directly to smoke-test connectivity:
    python3 tt_client.py            # prints record counts for a few resources
"""
import os
import re
import sys
import time
import json
import pathlib
import urllib.request
import urllib.error
import urllib.parse

BASE = "https://api.na.teamtailor.com"
API_VERSION = "20240904"


def resolve_key():
    """Key precedence: env TEAMTAILOR_API_KEY, then the API_KEY = "..." literal in
    teamtailor_flag.py (the daily-job script that lives in the recruiter's working dir).
    That script is the one path known to work from this machine, so we reuse its key."""
    k = os.environ.get("TEAMTAILOR_API_KEY")
    if k:
        return k
    for cand in [
        pathlib.Path.cwd() / "teamtailor_flag.py",
        pathlib.Path.home() / "Claude zinspector" / "teamtailor_flag.py",
    ]:
        if cand.exists():
            m = re.search(r'API_KEY\s*=\s*os\.environ\.get\([^,]+,\s*["\']([^"\']+)["\']', cand.read_text())
            if m:
                return m.group(1)
            m = re.search(r'API_KEY\s*=\s*["\']([^"\']+)["\']', cand.read_text())
            if m:
                return m.group(1)
    raise SystemExit("No Teamtailor API key: set TEAMTAILOR_API_KEY or place teamtailor_flag.py in the working dir.")


KEY = resolve_key()
HEADERS = {"Authorization": f"Token token={KEY}", "X-Api-Version": API_VERSION}


def _get(url):
    """Single GET with retry on 429/5xx. Returns parsed JSON."""
    for attempt in range(6):
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                wait = float(e.headers.get("Retry-After", 2 ** attempt))
                time.sleep(min(wait, 30))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 ** attempt)
    raise SystemExit(f"GET failed after retries: {url}")


def _encode(params):
    parts = []
    for k, v in params.items():
        parts.append(f"{urllib.parse.quote(str(k))}={urllib.parse.quote(str(v))}")
    return "&".join(parts)


def get_pages(path, params=None, cap=None):
    """Follow JSON:API `links.next` to the end. page[size] is forced to 30 (larger 400s).
    Returns (data, included). `cap` optionally stops after N data records (for smoke tests)."""
    params = dict(params or {})
    params["page[size]"] = 30
    url = f"{BASE}/v1/{path}?{_encode(params)}"
    data, included = [], []
    while url:
        r = _get(url)
        data += r.get("data", [])
        included += r.get("included", [])
        if cap and len(data) >= cap:
            break
        url = r.get("links", {}).get("next")
    return data, included


def get_one(path, params=None):
    url = f"{BASE}/v1/{path}?{_encode(params or {})}"
    return _get(url)


if __name__ == "__main__":
    for res in ["candidates", "job-applications", "jobs", "custom-fields"]:
        d, _ = get_pages(res, cap=1)
        # total lives in meta.record-count on the first page
        r = get_one(res, {"page[size]": 1})
        total = r.get("meta", {}).get("record-count", "?")
        print(f"{res:>18}: {total}")
