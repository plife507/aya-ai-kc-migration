#!/usr/bin/env python3
"""Find Jobber visits with no operational assignee.

Read-only wrapper around Jobber CLI v3 GraphQL queries. It reports:
- scheduled visits in a date range with no field/PP/truck assignee
- unscheduled visits, which cannot be scoped by day because startAt/endAt are null
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

JOBBER_REPO = Path("/home/plife507/Projects/jobber/jobber-cli-v3")
JOBBER_ENV_PATH = "/home/plife507/Projects/jobber/.env"
DEFAULT_TZ = "America/Los_Angeles"

VISITS_QUERY = """
query FindVisits($filter: VisitFilterAttributes, $cursor: String, $first: Int!) {
  visits(first: $first, after: $cursor, filter: $filter) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id
      title
      startAt
      endAt
      assignedUsers(first: 20) {
        nodes {
          id
          name { full }
        }
      }
      job {
        id
        jobNumber
        title
        jobType
        client { id name }
        property {
          address { street1 city province postalCode }
        }
      }
    }
  }
}
"""

JOB_VISITS_QUERY = """
query JobVisits($id: EncodedId!, $filter: VisitFilterAttributes) {
  job(id: $id) {
    id
    jobNumber
    title
    jobType
    client { id name }
    property {
      address { street1 city province postalCode }
    }
    visits(first: 100, filter: $filter) {
      pageInfo { hasNextPage endCursor }
      nodes {
        id
        title
        startAt
        endAt
        assignedUsers(first: 20) {
          nodes {
            id
            name { full }
          }
        }
      }
    }
  }
}
"""


class AuditError(RuntimeError):
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
    raise AuditError(f"Unsupported date format: {value!r}")


def day_boundary(value: date, tz_name: str) -> str:
    tz = ZoneInfo(tz_name)
    return datetime(value.year, value.month, value.day, tzinfo=tz).isoformat()


def parse_json_output(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    start = raw.find("{")
    if start > 0:
        raw = raw[start:]
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AuditError(f"Could not parse Jobber JSON output: {exc}") from exc


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
        raise AuditError(
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


def run_query(filter_payload: dict[str, Any], cursor: str | None = None, page_size: int = 40) -> dict[str, Any]:
    variables = {"filter": filter_payload, "cursor": cursor, "first": page_size}
    return run_graphql(VISITS_QUERY, variables)


def fetch_visits(
    filter_payload: dict[str, Any],
    max_visits: int | None = None,
    page_size: int = 40,
) -> tuple[list[dict[str, Any]], bool]:
    visits: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        data = run_query(filter_payload, cursor, page_size)
        conn = data.get("visits") or {}
        for node in conn.get("nodes") or []:
            if max_visits is not None and len(visits) >= max_visits:
                return visits, True
            visits.append(node)
        page_info = conn.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            return visits, False
        cursor = page_info.get("endCursor")
        if not cursor:
            return visits, True


def assigned_names(visit: dict[str, Any]) -> list[str]:
    users = ((visit.get("assignedUsers") or {}).get("nodes") or [])
    names = []
    for user in users:
        name = (((user.get("name") or {}).get("full")) or "").strip()
        if name:
            names.append(name)
    return names


def is_hq_user(name: str) -> bool:
    return name.strip().lower().startswith("hq -")


def normalize_visit(visit: dict[str, Any]) -> dict[str, Any]:
    job = visit.get("job") or {}
    client = job.get("client") or {}
    prop = job.get("property") or {}
    address = prop.get("address") or {}
    names = assigned_names(visit)
    operational = [name for name in names if not is_hq_user(name)]
    return {
        "jobNumber": job.get("jobNumber"),
        "client": client.get("name"),
        "clientId": client.get("id"),
        "jobTitle": job.get("title"),
        "jobType": job.get("jobType"),
        "visitTitle": visit.get("title"),
        "startAt": visit.get("startAt"),
        "endAt": visit.get("endAt"),
        "visitId": visit.get("id"),
        "jobId": job.get("id"),
        "assignedUsers": names,
        "operationalAssignees": operational,
        "address": {
            "street1": address.get("street1"),
            "city": address.get("city"),
            "province": address.get("province"),
            "postalCode": address.get("postalCode"),
        },
    }


def no_operational_assignee(visit: dict[str, Any], strict_empty: bool) -> bool:
    names = assigned_names(visit)
    if strict_empty:
        return len(names) == 0
    return not any(not is_hq_user(name) for name in names)


def resolve_job_id(job_number: int) -> str:
    data = run_cli(["search", "jobs", str(job_number), "--json"])
    matches = [item for item in data.get("items") or [] if item.get("jobNumber") == job_number]
    if not matches:
        raise AuditError(f"Could not resolve exact Jobber job #{job_number}")
    return str(matches[0]["id"])


def fetch_job_visits(job_number: int, filter_payload: dict[str, Any]) -> list[dict[str, Any]]:
    job_id = resolve_job_id(job_number)
    data = run_graphql(JOB_VISITS_QUERY, {"id": job_id, "filter": filter_payload})
    job = data.get("job") or {}
    visits = ((job.get("visits") or {}).get("nodes") or [])
    return [{**visit, "job": job} for visit in visits]


def local_date(value: str | None, tz_name: str) -> str | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(ZoneInfo(tz_name)).date().isoformat()


def group_by_day(visits: list[dict[str, Any]], tz_name: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for visit in visits:
        key = local_date(visit.get("startAt"), tz_name) or "unscheduled"
        grouped.setdefault(key, []).append(visit)
    return [
        {
            "date": key,
            "count": len(items),
            "jobs": sorted(
                [
                    {
                        "jobNumber": item.get("jobNumber"),
                        "client": item.get("client"),
                        "jobTitle": item.get("jobTitle"),
                        "visitTitle": item.get("visitTitle"),
                        "startAt": item.get("startAt"),
                        "visitId": item.get("visitId"),
                    }
                    for item in items
                ],
                key=lambda item: (item.get("startAt") or "", item.get("jobNumber") or 0),
            ),
        }
        for key, items in sorted(grouped.items())
    ]


def group_job_numbers_by_day(visits: list[dict[str, Any]], tz_name: str) -> list[dict[str, Any]]:
    grouped: dict[str, set[int]] = {}
    for visit in visits:
        job_number = visit.get("jobNumber")
        if job_number is None:
            continue
        key = local_date(visit.get("startAt"), tz_name) or "unscheduled"
        grouped.setdefault(key, set()).add(int(job_number))
    return [
        {
            "date": key,
            "jobCount": len(job_numbers),
            "jobNumbers": sorted(job_numbers),
        }
        for key, job_numbers in sorted(grouped.items())
    ]


def fetch_scheduled_day_by_day(
    start_date: date,
    end_date: date,
    tz_name: str,
    page_size: int,
) -> tuple[list[dict[str, Any]], bool]:
    visits: list[dict[str, Any]] = []
    truncated = False
    current = start_date
    while current < end_date:
        next_day = current + timedelta(days=1)
        day_filter = {
            "startAt": {
                "after": day_boundary(current, tz_name),
                "before": day_boundary(next_day, tz_name),
            }
        }
        day_visits, day_truncated = fetch_visits(day_filter, page_size=page_size)
        visits.extend(day_visits)
        truncated = truncated or day_truncated
        current = next_day
    return visits, truncated


def main() -> int:
    parser = argparse.ArgumentParser(description="Find scheduled/unscheduled Jobber visits with no operational assignee.")
    parser.add_argument("--from", dest="from_date", default=None, help="Start date, default today in America/Los_Angeles.")
    parser.add_argument("--to", dest="to_date", default=None, help="Exclusive end date. Defaults to --from + --days.")
    parser.add_argument("--days", type=int, default=365, help="Date range length when --to is omitted. Default: 365.")
    parser.add_argument("--timezone", default=DEFAULT_TZ, help=f"Date boundary timezone. Default: {DEFAULT_TZ}.")
    parser.add_argument("--no-unscheduled", action="store_true", help="Skip status=UNSCHEDULED scan.")
    parser.add_argument("--max-unscheduled", type=int, default=1000, help="Cap unscheduled visits scanned. Default: 1000.")
    parser.add_argument("--page-size", type=int, default=40, help="GraphQL visit page size. Lower this if Jobber throttles. Default: 40.")
    parser.add_argument("--strict-empty", action="store_true", help="Only flag visits with zero assignedUsers, instead of ignoring HQ users.")
    parser.add_argument("--job-numbers-only", action="store_true", help="Emit only unique job numbers needing attention.")
    parser.add_argument("--job-numbers", nargs="+", type=int, help="Limit the dated scan to exact job numbers. Faster for follow-up day-by-day checks.")
    parser.add_argument("--group-by-day", action="store_true", help="Add a dated grouping of scheduled unassigned visits.")
    parser.add_argument("--day-by-day", action="store_true", help="Fetch scheduled visits one calendar day at a time to reduce throttling and make date grouping explicit.")
    parser.add_argument("--output-json", help="Write the full JSON payload to this path instead of only printing stdout.")
    args = parser.parse_args()

    if args.days <= 0:
        parser.error("--days must be positive")
    if args.max_unscheduled <= 0:
        parser.error("--max-unscheduled must be positive")
    if args.page_size <= 0:
        parser.error("--page-size must be positive")

    start_date = parse_date(args.from_date) if args.from_date else datetime.now(ZoneInfo(args.timezone)).date()
    end_date = parse_date(args.to_date) if args.to_date else start_date + timedelta(days=args.days)
    if end_date <= start_date:
        parser.error("--to must be after --from")

    scheduled_filter = {
        "startAt": {
            "after": day_boundary(start_date, args.timezone),
            "before": day_boundary(end_date, args.timezone),
        }
    }
    if args.job_numbers:
        scheduled = []
        for job_number in args.job_numbers:
            scheduled.extend(fetch_job_visits(job_number, scheduled_filter))
        scheduled_truncated = False
    elif args.day_by_day:
        scheduled, scheduled_truncated = fetch_scheduled_day_by_day(
            start_date,
            end_date,
            args.timezone,
            args.page_size,
        )
    else:
        scheduled, scheduled_truncated = fetch_visits(scheduled_filter, page_size=args.page_size)
    scheduled_unassigned = [
        normalize_visit(visit)
        for visit in scheduled
        if no_operational_assignee(visit, args.strict_empty)
    ]

    unscheduled: list[dict[str, Any]] = []
    unscheduled_truncated = False
    if not args.no_unscheduled:
        raw_unscheduled, unscheduled_truncated = fetch_visits(
            {"status": "UNSCHEDULED"},
            max_visits=args.max_unscheduled,
            page_size=args.page_size,
        )
        unscheduled = [
            normalize_visit(visit)
            for visit in raw_unscheduled
            if no_operational_assignee(visit, args.strict_empty)
        ]

    unique_job_numbers = sorted(
        {
            item["jobNumber"]
            for item in [*scheduled_unassigned, *unscheduled]
            if item.get("jobNumber") is not None
        }
    )
    if args.job_numbers_only:
        print(json.dumps(unique_job_numbers, indent=2))
        return 0

    payload = {
        "ok": True,
        "timezone": args.timezone,
        "mode": "strict-empty" if args.strict_empty else "no-operational-assignee",
        "scanMode": "job-numbers" if args.job_numbers else "day-by-day" if args.day_by_day else "range",
        "range": {
            "from": start_date.isoformat(),
            "toExclusive": end_date.isoformat(),
            "days": (end_date - start_date).days,
        },
        "pageSize": args.page_size,
        "scheduled": {
            "scanned": len(scheduled),
            "truncated": scheduled_truncated,
            "unassignedCount": len(scheduled_unassigned),
            "unassigned": scheduled_unassigned,
            "byDay": group_by_day(scheduled_unassigned, args.timezone) if args.group_by_day else None,
            "jobNumbersByDay": group_job_numbers_by_day(scheduled_unassigned, args.timezone),
        },
        "unscheduled": {
            "scannedCap": None if args.no_unscheduled else args.max_unscheduled,
            "skipped": args.no_unscheduled,
            "truncated": unscheduled_truncated,
            "unassignedCount": len(unscheduled),
            "unassigned": unscheduled,
            "uniqueJobNumbers": sorted(
                {
                    int(item["jobNumber"])
                    for item in unscheduled
                    if item.get("jobNumber") is not None
                }
            ),
        },
        "uniqueJobNumbers": unique_job_numbers,
    }
    encoded = json.dumps(payload, indent=2)
    if args.output_json:
        output_path = Path(args.output_json).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(encoded + "\n", encoding="utf-8")
        print(json.dumps({"ok": True, "outputJson": str(output_path), "uniqueJobNumbers": unique_job_numbers}, indent=2))
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(1)
