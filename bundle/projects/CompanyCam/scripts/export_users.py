#!/usr/bin/env python3
"""Export CompanyCam users for local matching.

This script only calls GET /users and writes ignored local files under exports/.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


BASE_URL = "https://api.companycam.com/v2"
PER_PAGE = 100


CSV_FIELDS = [
    "id",
    "first_name",
    "last_name",
    "display_name",
    "email_address",
    "phone_number",
    "status",
    "user_role",
    "user_url",
    "company_id",
    "created_at",
    "updated_at",
]


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


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


def display_name(user: dict[str, Any]) -> str:
    first = str(user.get("first_name") or "").strip()
    last = str(user.get("last_name") or "").strip()
    full = f"{first} {last}".strip()
    return full or str(user.get("email_address") or user.get("id") or "")


def flatten_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": user.get("id"),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "display_name": display_name(user),
        "email_address": user.get("email_address"),
        "phone_number": user.get("phone_number"),
        "status": user.get("status"),
        "user_role": user.get("user_role"),
        "user_url": user.get("user_url"),
        "company_id": user.get("company_id"),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
    }


def fetch_all_users(token: str) -> list[dict[str, Any]]:
    users: list[dict[str, Any]] = []
    page = 1
    while True:
        batch = api_get(token, "/users", {"page": page, "per_page": PER_PAGE})
        if not isinstance(batch, list):
            raise RuntimeError(f"Unexpected /users response on page {page}: {type(batch).__name__}")
        if not batch:
            break
        users.extend(user for user in batch if isinstance(user, dict))
        if len(batch) < PER_PAGE:
            break
        page += 1
    return users


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")

    token = os.environ.get("COMPANYCAM_API_TOKEN")
    if not token:
        print("Missing COMPANYCAM_API_TOKEN. Create .env from .env.example first.", file=sys.stderr)
        return 2

    export_dir = repo_root / "exports"
    export_dir.mkdir(exist_ok=True)

    users = fetch_all_users(token)
    users.sort(key=lambda user: (display_name(user).lower(), str(user.get("email_address") or "")))

    json_path = export_dir / "companycam_users.json"
    csv_path = export_dir / "companycam_users.csv"

    json_path.write_text(json.dumps(users, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for user in users:
            writer.writerow(flatten_user(user))

    active = sum(1 for user in users if user.get("status") == "active")
    print(f"Exported {len(users)} CompanyCam users ({active} active).")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
