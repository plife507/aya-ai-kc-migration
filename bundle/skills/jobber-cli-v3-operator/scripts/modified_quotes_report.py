#!/usr/bin/env python3
"""Report Jobber quotes modified per day.

Read-only wrapper around Jobber CLI v3 GraphQL queries. It groups quotes by the
local date of Jobber's Quote.updatedAt timestamp.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

JOBBER_REPO = Path("/home/plife507/Projects/jobber/jobber-cli-v3")
JOBBER_ENV_PATH = "/home/plife507/Projects/jobber/.env"
DEFAULT_TZ = "America/Los_Angeles"

QUOTES_QUERY = """
query QuotesModified($filter: QuoteFilterAttributes, $cursor: String, $first: Int!) {
  quotes(first: $first, after: $cursor, filter: $filter) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id
      quoteNumber
      title
      quoteStatus
      createdAt
      updatedAt
      sentAt
      transitionedAt
      jobberWebUri
      amounts { total }
      client { id name }
      property {
        address { street1 city province postalCode }
      }
    }
  }
}
"""


class ReportError(RuntimeError):
    pass


def parse_date(value: str) -> date:
    value = value.strip()
    current_year = datetime.now(ZoneInfo(DEFAULT_TZ)).year
    for pattern, add_year in [
        ("%Y-%m-%d", False),
        ("%m/%d/%Y", False),
        ("%m-%d-%Y", False),
        ("%Y/%m/%d", False),
        ("%m/%d", True),
        ("%m-%d", True),
    ]:
        try:
            parsed = datetime.strptime(value, pattern).date()
            if add_year:
                parsed = parsed.replace(year=current_year)
            return parsed
        except ValueError:
            continue
    raise ReportError(f"Unsupported date format: {value!r}")


def local_day_start(value: date, tz_name: str) -> datetime:
    return datetime.combine(value, time.min, ZoneInfo(tz_name))


def parse_jobber_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_json_output(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    start = raw.find("{")
    if start > 0:
        raw = raw[start:]
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ReportError(f"Could not parse Jobber JSON output: {exc}") from exc


def run_cli(args: list[str]) -> dict[str, Any]:
    env = os.environ.copy()
    env["JOBBER_ENV_PATH"] = JOBBER_ENV_PATH
    env["JOBBER_OAUTH_SKIP_AUTHORIZE"] = "1"
    proc = subprocess.run(
        ["yarn", "dev", *args],
        cwd=JOBBER_REPO,
        env=env,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise ReportError(
            f"Jobber CLI failed ({proc.returncode})\nSTDERR:\n{proc.stderr.strip()}\nSTDOUT:\n{proc.stdout.strip()}"
        )
    return parse_json_output(proc.stdout)


def run_graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    return run_cli(
        [
            "query",
            query,
            "--variables",
            json.dumps(variables, separators=(",", ":")),
            "--json",
        ]
    )


def fetch_quotes(
    start_date: date,
    end_date_exclusive: date,
    tz_name: str,
    page_size: int,
    max_quotes: int | None,
) -> tuple[list[dict[str, Any]], bool]:
    after = local_day_start(start_date, tz_name).isoformat()
    before = local_day_start(end_date_exclusive, tz_name).isoformat()
    filter_payload = {"updatedAt": {"after": after, "before": before}}
    quotes: list[dict[str, Any]] = []
    cursor: str | None = None
    truncated = False

    while True:
        data = run_graphql(
            QUOTES_QUERY,
            {"filter": filter_payload, "cursor": cursor, "first": page_size},
        )
        conn = data.get("quotes") or {}
        for node in conn.get("nodes") or []:
            if max_quotes is not None and len(quotes) >= max_quotes:
                return quotes, True
            quotes.append(node)

        page_info = conn.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            truncated = True
            break

    return quotes, truncated


def normalize_quote(quote: dict[str, Any], tz_name: str) -> dict[str, Any]:
    updated_at = parse_jobber_datetime(quote["updatedAt"]).astimezone(ZoneInfo(tz_name))
    client = quote.get("client") or {}
    address = ((quote.get("property") or {}).get("address") or {})
    amount = quote.get("amounts") or {}
    return {
        "localDate": updated_at.date().isoformat(),
        "localUpdatedAt": updated_at.isoformat(timespec="seconds"),
        "quoteNumber": quote.get("quoteNumber"),
        "client": client.get("name"),
        "title": quote.get("title"),
        "status": quote.get("quoteStatus"),
        "total": amount.get("total"),
        "url": quote.get("jobberWebUri"),
        "createdAt": quote.get("createdAt"),
        "sentAt": quote.get("sentAt"),
        "address": {
            "street1": address.get("street1"),
            "city": address.get("city"),
            "province": address.get("province"),
            "postalCode": address.get("postalCode"),
        },
    }


def money(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"${value:,.2f}"
    return "$0.00"


def render_text(report: dict[str, Any]) -> str:
    lines = [
        f"Modified quotes by day ({report['timezone']})",
        f"Range: {report['from']} through {report['toInclusive']}",
        "",
    ]
    for day in report["days"]:
        lines.append(f"{day['date']} - {day['count']} quote(s)")
        for quote in day["quotes"]:
            parts = [
                f"#{quote['quoteNumber']}",
                quote.get("client") or "Unknown client",
                quote.get("title") or "Untitled",
                quote.get("status") or "unknown",
                money(quote.get("total")),
                quote.get("localUpdatedAt") or "",
            ]
            lines.append("  - " + " | ".join(parts))
        lines.append("")
    if report["truncated"]:
        lines.append("Result truncated before all matching quotes were fetched.")
    if report["totalQuotes"] == 0:
        lines.append("No modified quotes found.")
    return "\n".join(lines).rstrip()


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    tz_name = args.tz
    start = parse_date(args.from_date)
    if args.to:
        end_inclusive = parse_date(args.to)
    elif args.days:
        end_inclusive = start + timedelta(days=args.days - 1)
    else:
        end_inclusive = start

    if end_inclusive < start:
        raise ReportError("--to must be the same as or later than --from")

    quotes, truncated = fetch_quotes(
        start,
        end_inclusive + timedelta(days=1),
        tz_name,
        args.page_size,
        args.max_quotes,
    )
    normalized = [normalize_quote(quote, tz_name) for quote in quotes]
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for quote in normalized:
        buckets[quote["localDate"]].append(quote)

    days = []
    cursor = start
    while cursor <= end_inclusive:
        key = cursor.isoformat()
        items = sorted(buckets.get(key, []), key=lambda q: q["localUpdatedAt"], reverse=True)
        days.append({"date": key, "count": len(items), "quotes": items})
        cursor += timedelta(days=1)

    return {
        "timezone": tz_name,
        "from": start.isoformat(),
        "toInclusive": end_inclusive.isoformat(),
        "totalQuotes": len(normalized),
        "truncated": truncated,
        "days": days,
    }


def main(argv: list[str]) -> int:
    today = datetime.now(ZoneInfo(DEFAULT_TZ)).date()
    parser = argparse.ArgumentParser(description="Report Jobber quotes modified per day.")
    parser.add_argument("--from", dest="from_date", default=today.isoformat(), help="Start date, default today")
    parser.add_argument("--to", help="Inclusive end date")
    parser.add_argument("--days", type=int, help="Number of days starting at --from")
    parser.add_argument("--tz", default=DEFAULT_TZ, help=f"Timezone for day grouping, default {DEFAULT_TZ}")
    parser.add_argument("--page-size", type=int, default=25, help="GraphQL page size, default 25")
    parser.add_argument("--max-quotes", type=int, help="Stop after this many quotes")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args(argv)

    if args.days is not None and args.days < 1:
        raise ReportError("--days must be at least 1")
    if args.to and args.days:
        raise ReportError("Use either --to or --days, not both")

    report = build_report(args)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except ReportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
