#!/usr/bin/env python3
"""Read-only CompanyCam API smoke check.

This script intentionally only calls GET endpoints:
- /company
- /users/current
- /projects
- /checklists
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


BASE_URL = "https://api.companycam.com/v2"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def api_get(token: str, path: str, params: dict[str, Any] | None = None) -> Any:
    query = ""
    if params:
        query = "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{BASE_URL}{path}{query}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else None
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GET {path} failed: HTTP {error.code} {body}") from error


def pick_name(record: Any) -> str:
    if not isinstance(record, dict):
        return "(unknown)"
    for key in ("name", "display_name", "company_name", "email_address", "email"):
        value = record.get(key)
        if value:
            return str(value)
    first = record.get("first_name")
    last = record.get("last_name")
    if first or last:
        return f"{first or ''} {last or ''}".strip()
    return str(record.get("id") or "(unknown)")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")

    token = os.environ.get("COMPANYCAM_API_TOKEN")
    if not token:
        print("Missing COMPANYCAM_API_TOKEN. Create .env from .env.example first.", file=sys.stderr)
        return 2

    company = api_get(token, "/company")
    current_user = api_get(token, "/users/current")
    projects = api_get(token, "/projects", {"page": 1, "per_page": 5})
    checklists = api_get(token, "/checklists", {"page": 1, "per_page": 5})

    print("CompanyCam read-only check passed.")
    print(f"Company: {pick_name(company)}")
    print(f"Current user: {pick_name(current_user)}")

    if isinstance(projects, list):
        print(f"Projects returned: {len(projects)}")
        for project in projects[:5]:
            print(f"- {pick_name(project)}")
    else:
        print("Projects returned: non-list response")

    if isinstance(checklists, list):
        print(f"Checklists returned: {len(checklists)}")
        for checklist in checklists[:5]:
            print(f"- {pick_name(checklist)}")
    else:
        print("Checklists returned: non-list response")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
