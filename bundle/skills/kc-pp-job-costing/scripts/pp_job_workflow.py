#!/usr/bin/env python3
"""Repeatable KC PP job workflow.

Dry-run by default. With --apply it creates the missing Jobber subcontractor
expense and applies CompanyCam project/checklist/user writes. Slack is not sent
from this script; it emits the exact body for the OpenClaw Slack send lane.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

JOBBER_REPO = Path("/home/plife507/Projects/jobber/jobber-cli-v3")
JOBBER_ENV_PATH = "/home/plife507/Projects/jobber/.env"
COMPANYCAM_REPO = Path("/home/plife507/Projects/CompanyCam")
COMPANYCAM_ENV_PATH = "/home/plife507/Projects/CompanyCam/.env"
EXPENSE_WRAPPER = "/home/plife507/AYA-CLAW/skills/jobber-cli-v3-operator/scripts/create_subcontractor_expense.py"
DEFAULT_CHECKLIST_ID = "61791"
GENERAL_MISC_CHECKLIST_ID = "52548"
REVISIT_CHECKLIST_ID = "181128"
DEFAULT_SLACK_CHANNEL_ID = "C08CTUF1T7C"
DEFAULT_SLACK_CHANNEL_NAME = "#pp-dispatch-mgmt"
ASSIGNMENT_REGISTRY_PATH = Path(__file__).resolve().parents[1] / "references/pp-companycam-assignments.json"
COMPANYCAM_PROJECT_SEARCH_PAGE_SIZE = 25
COMPANYCAM_PROJECT_REVIEW_NAME_RE = re.compile(
    r"\b(job\s*walk|jobwalk|walk\s*through|walkthrough|walk\s*thru|estimate|quote|bid)\b",
    re.IGNORECASE,
)


class FlowError(RuntimeError):
    pass


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        env={**os.environ, **(env or {})},
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise FlowError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\n"
            f"STDERR:\n{proc.stderr.strip()}\nSTDOUT:\n{proc.stdout.strip()}"
        )
    return proc.stdout


def parse_json(text: str) -> Any:
    raw = text.strip()
    for marker in ("{", "["):
        idx = raw.find(marker)
        if idx >= 0:
            try:
                return json.loads(raw[idx:])
            except json.JSONDecodeError:
                pass
    raise FlowError(f"Could not parse JSON output:\n{raw}")


def jobber_env(writes: bool = False) -> dict[str, str]:
    env = {"JOBBER_ENV_PATH": JOBBER_ENV_PATH, "JOBBER_OAUTH_SKIP_AUTHORIZE": "1"}
    if writes:
        env["JOBBER_WRITES_ENABLED"] = "1"
    return env


def companycam_env(writes: bool = False) -> dict[str, str]:
    env = {"COMPANYCAM_ENV_PATH": COMPANYCAM_ENV_PATH}
    if writes:
        env["COMPANYCAM_WRITES_ENABLED"] = "1"
    return env


def amount(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace("$", "").replace(",", ""))


def money(value: float) -> str:
    return f"${value:,.2f}"


def normalize_date(value: str) -> tuple[str, str]:
    value = value.strip()
    current_year = datetime.now().year
    for pattern, add_year in [
        ("%Y-%m-%d", False),
        ("%m/%d/%Y", False),
        ("%m-%d-%Y", False),
        ("%Y/%m/%d", False),
        ("%m/%d", True),
        ("%m-%d", True),
    ]:
        try:
            dt = datetime.strptime(value, pattern)
            if add_year:
                dt = dt.replace(year=current_year)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%-m/%-d/%Y")
        except ValueError:
            continue
    raise FlowError(f"Unsupported date format: {value!r}")


def default_checklist_for_kind(kind: str) -> str:
    normalized = str(kind or "").lower()
    if "revisit" in normalized:
        return REVISIT_CHECKLIST_ID
    if "recurring" in normalized:
        return GENERAL_MISC_CHECKLIST_ID
    return DEFAULT_CHECKLIST_ID


def gid_number(gid: str) -> str | None:
    try:
        decoded = base64.b64decode(gid).decode("utf-8")
    except Exception:
        return None
    tail = decoded.rsplit("/", 1)[-1]
    return tail if tail.isdigit() else None


def state_abbrev(value: Any) -> str:
    states = {"california": "CA"}
    raw = str(value or "").strip()
    return states.get(raw.lower(), raw)


def display_location(address: dict[str, Any]) -> str:
    street_parts = [
        address.get("street1") or address.get("street_address_1"),
        address.get("street2") or address.get("street_address_2"),
    ]
    street = " ".join(str(part).strip() for part in street_parts if str(part or "").strip())
    city = str(address.get("city") or "").strip()
    state = state_abbrev(address.get("province") or address.get("state"))
    postal = str(address.get("postalCode") or address.get("postal_code") or "").strip()
    city_line = ", ".join(part for part in [city, " ".join(part for part in [state, postal] if part)] if part)
    return ", ".join(part for part in [street, city_line] if part)


def tokens(value: str) -> list[str]:
    stop = {"pp", "sub", "subcon", "washpros", "wash", "pros", "the", "and"}
    return [t for t in re.findall(r"[a-z0-9]+", value.lower()) if len(t) >= 2 and t not in stop]


def identity_key(value: str) -> str:
    return " ".join(tokens(value))


def load_pp_assignments() -> list[dict[str, Any]]:
    if not ASSIGNMENT_REGISTRY_PATH.exists():
        return []
    payload = json.loads(ASSIGNMENT_REGISTRY_PATH.read_text())
    return payload.get("assignments", [])


def match_pp_assignment(sub: str) -> dict[str, Any] | None:
    needle = identity_key(sub)
    if not needle:
        return None
    matches: list[dict[str, Any]] = []
    for assignment in load_pp_assignments():
        aliases = assignment.get("aliases") or []
        keys = {identity_key(str(alias)) for alias in aliases}
        keys.add(identity_key(str(assignment.get("slackSub") or "")))
        keys.add(identity_key(str(assignment.get("expenseVendor") or "")))
        if needle in keys:
            matches.append(assignment)
    if len(matches) > 1:
        options = ", ".join(str(item.get("key")) for item in matches)
        raise FlowError(f"PP assignment match is ambiguous for {sub!r}: {options}")
    return matches[0] if matches else None


def explicit_companycam_users(raw: str | None) -> list[dict[str, Any]]:
    if not raw:
        return []
    ids = [part.strip() for part in re.split(r"[,\s]+", raw) if part.strip()]
    return [{"id": user_id, "matchedBy": "explicit-id"} for user_id in ids]


def registry_companycam_users(assignment: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not assignment:
        return []
    users = []
    for user in assignment.get("companyCamUsers") or []:
        if not user.get("id"):
            continue
        users.append({**user, "id": str(user["id"]), "matchedBy": f"registry:{assignment.get('key')}"})
    return users


def unique_companycam_users(users: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique = []
    for user in users:
        user_id = str(user.get("id") or "").strip()
        if not user_id or user_id in seen:
            continue
        seen.add(user_id)
        unique.append({**user, "id": user_id})
    return unique


def find_companycam_user(query: str, explicit_id: str | None) -> dict[str, Any] | None:
    if explicit_id:
        return {"id": explicit_id, "matchedBy": "explicit-id"}
    export_path = COMPANYCAM_REPO / "exports/companycam_users.json"
    if not export_path.exists():
        run(["npm", "run", "dev", "--", "users", "export", "--json"], COMPANYCAM_REPO, companycam_env())
    users = json.loads(export_path.read_text())
    q_tokens = tokens(query)
    if not q_tokens:
        return None
    scored: list[tuple[int, dict[str, Any]]] = []
    for user in users:
        if str(user.get("status", "")).lower() != "active":
            continue
        hay = " ".join(str(user.get(k) or "") for k in ("first_name", "last_name", "display_name", "email_address"))
        hay_tokens = set(tokens(hay))
        score = sum(1 for token in q_tokens if token in hay_tokens)
        if score:
            scored.append((score, user))
    if not scored:
        return None
    scored.sort(key=lambda item: (item[0], str(item[1].get("updated_at") or "")), reverse=True)
    top_score = scored[0][0]
    top = [user for score, user in scored if score == top_score]
    if len(top) > 1:
        options = ", ".join(f"{u.get('id')}:{u.get('first_name')} {u.get('last_name')}" for u in top[:5])
        raise FlowError(f"CompanyCam user match is ambiguous for {query!r}: {options}")
    user = top[0]
    return {
        "id": str(user.get("id")),
        "name": " ".join(str(user.get(k) or "").strip() for k in ("first_name", "last_name")).strip(),
        "email": user.get("email_address"),
        "matchedBy": "token-score",
    }


def resolve_companycam_users(args: argparse.Namespace, assignment: dict[str, Any] | None) -> list[dict[str, Any]]:
    if args.skip_companycam:
        return []

    explicit_users = explicit_companycam_users(args.companycam_user_id)
    if explicit_users:
        return unique_companycam_users(explicit_users)

    if args.companycam_user_query:
        if args.apply:
            raise FlowError(
                "Live CompanyCam assignment cannot use --companycam-user-query. "
                "Add the PP to references/pp-companycam-assignments.json or pass --companycam-user-id."
            )
        user = find_companycam_user(args.companycam_user_query, None)
        if not user:
            raise FlowError(f"No active CompanyCam user matched --companycam-user-query {args.companycam_user_query!r}")
        return unique_companycam_users([{**user, "matchedBy": f"explicit-query:{args.companycam_user_query}"}])

    users = registry_companycam_users(assignment)
    if users:
        return unique_companycam_users(users)

    raise FlowError(
        "No reviewed CompanyCam user assignment resolved. CompanyCam assignment is strict by default: "
        "add this PP to references/pp-companycam-assignments.json or pass --companycam-user-id."
    )


def resolve_job(job_number: str) -> dict[str, Any]:
    search = parse_json(run(["yarn", "dev", "search", "jobs", job_number, "--json"], JOBBER_REPO, jobber_env()))
    matches = [item for item in search.get("items", []) if str(item.get("jobNumber")) == str(job_number)]
    if len(matches) != 1:
        raise FlowError(f"Expected one exact Jobber job match for {job_number}, found {len(matches)}")
    query = """
    query($id: EncodedId!) {
      job(id: $id) {
        id jobNumber title total jobStatus jobType
        client { id name }
        property { id address { street1 street2 city province postalCode country } }
        quote { id quoteNumber amounts { subtotal discountAmount total } }
        customFields {
          ... on CustomFieldText {
            id label
            customFieldConfiguration { id name }
            valueText
          }
          ... on CustomFieldLink {
            id label
            customFieldConfiguration { id name }
            valueLink { text url }
          }
        }
        visits(first: 5) { nodes { id title startAt endAt } }
      }
    }
    """
    return parse_json(
        run(
            ["yarn", "dev", "query", query, "--variables", json.dumps({"id": matches[0]["id"]}), "--json"],
            JOBBER_REPO,
            jobber_env(),
        )
    )["job"]


def list_expenses(job_number: str) -> list[dict[str, Any]]:
    payload = parse_json(run(["yarn", "dev", "job-expense", "list", job_number, "--json"], JOBBER_REPO, jobber_env()))
    return payload.get("expenses", [])


def matching_expense(expenses: list[dict[str, Any]], sub: str, sub_pay: float, iso_date: str) -> dict[str, Any] | None:
    vendor_key = sub.lower().split(" - ")[0].strip()
    for expense in expenses:
        if str(expense.get("title") or "").lower() != "sub":
            continue
        if abs(amount(expense.get("total")) - sub_pay) >= 0.01:
            continue
        if str(expense.get("date") or "")[:10] != iso_date:
            continue
        if vendor_key and vendor_key not in str(expense.get("description") or "").lower():
            continue
        return expense
    return None


def create_expense(job_number: str, sub: str, pay: str, date_display: str, reason: str) -> dict[str, Any]:
    payload = parse_json(
        run(
            [
                "python3",
                EXPENSE_WRAPPER,
                job_number,
                "--vendor",
                sub,
                "--amount",
                pay,
                "--date",
                date_display,
                "--reason",
                reason,
            ],
            Path("/home/plife507/AYA-CLAW/kc"),
        )
    )
    return payload.get("expense", payload)


def sync_companycam(job_number: str, title: str, address: dict[str, Any], checklist_id: str, apply: bool) -> dict[str, Any]:
    cmd = [
        "npm", "run", "dev", "--", "projects", "sync-job",
        "--job-number", job_number,
        "--title", title,
        "--street-address-1", address.get("street1") or "",
        "--city", address.get("city") or "",
        "--state", address.get("province") or "",
        "--postal-code", address.get("postalCode") or "",
        "--checklist-template-id", checklist_id,
        "--json",
    ]
    if not apply:
        cmd.insert(-1, "--dry-run")
    return parse_json(run(cmd, COMPANYCAM_REPO, companycam_env(writes=apply)))


def match_companycam(address: dict[str, Any]) -> dict[str, Any]:
    cmd = [
        "npm", "run", "dev", "--", "projects", "match",
        "--street-address-1", address.get("street1") or "",
        "--city", address.get("city") or "",
        "--state", address.get("province") or "",
        "--postal-code", address.get("postalCode") or "",
        "--json",
    ]
    return parse_json(run(cmd, COMPANYCAM_REPO, companycam_env()))


def custom_field_name(field: dict[str, Any]) -> str:
    config = field.get("customFieldConfiguration") if isinstance(field.get("customFieldConfiguration"), dict) else {}
    return str(config.get("name") or field.get("label") or "")


def custom_field_value(field: dict[str, Any]) -> str:
    link = field.get("valueLink") if isinstance(field.get("valueLink"), dict) else {}
    return str(link.get("url") or link.get("text") or field.get("valueText") or "").strip()


def companycam_project_id_from_job(job: dict[str, Any]) -> str | None:
    for field in job.get("customFields") or []:
        if not isinstance(field, dict):
            continue
        if "company cam" not in custom_field_name(field).lower().replace("companycam", "company cam"):
            continue
        value = custom_field_value(field)
        if not value:
            continue
        url_match = re.search(r"companycam\.com/(?:embed/)?projects/(\d+)", value, re.IGNORECASE)
        if url_match:
            return url_match.group(1)
        if re.fullmatch(r"\d{5,}", value):
            return value
    return None


def normalized_component(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def address_component(address: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = address.get(key)
        if value:
            return str(value)
    return ""


def matching_components_agree(job_address: dict[str, Any], companycam_address: dict[str, Any]) -> bool:
    checks = [
        ("city", ("city",)),
        ("province", ("state", "province")),
        ("postalCode", ("postal_code", "postalCode")),
    ]
    for job_key, cc_keys in checks:
        job_value = normalized_component(job_address.get(job_key))
        cc_value = normalized_component(address_component(companycam_address, *cc_keys))
        if not job_value or not cc_value or job_value != cc_value:
            return False
    return True


def project_name_needs_review(project: dict[str, Any]) -> bool:
    return bool(COMPANYCAM_PROJECT_REVIEW_NAME_RE.search(str(project.get("name") or "")))


def select_companycam_project_match(cc_match: dict[str, Any], job_address: dict[str, Any]) -> dict[str, Any]:
    matches = cc_match.get("matches") or []
    if cc_match.get("candidates", 0) >= COMPANYCAM_PROJECT_SEARCH_PAGE_SIZE:
        raise FlowError(
            "CompanyCam project search returned a full page of candidates; refusing to trust a possibly truncated match. "
            "Pass --companycam-project-id after review.\n"
            f"{json.dumps(cc_match, indent=2)}"
        )
    if cc_match.get("status") != "matched" or len(matches) != 1:
        if cc_match.get("status") == "ambiguous":
            raise FlowError(
                "CompanyCam project match is ambiguous; pass --companycam-project-id after review:\n"
                f"{json.dumps(cc_match, indent=2)}"
            )
        raise FlowError(
            "No safe matching CompanyCam project found. Re-run with --create-companycam-project "
            "only after confirming a new album is correct, or pass --companycam-project-id for the existing album.\n"
            f"{json.dumps(cc_match, indent=2)}"
        )

    project = matches[0]
    match_type = str(project.get("matchType") or "")
    project_address = project.get("address") if isinstance(project.get("address"), dict) else {}
    if match_type == "line1" and not matching_components_agree(job_address, project_address):
        raise FlowError(
            "CompanyCam project matched only on street line 1, but city/state/ZIP were not fully verified. "
            "Pass --companycam-project-id after review.\n"
            f"{json.dumps(cc_match, indent=2)}"
        )
    if match_type not in {"exact", "line1"}:
        raise FlowError(
            f"CompanyCam project match type {match_type!r} is not approved for automatic PP writes. "
            "Pass --companycam-project-id after review.\n"
            f"{json.dumps(cc_match, indent=2)}"
        )
    if project_name_needs_review(project):
        raise FlowError(
            "CompanyCam matched a jobwalk/estimate-style album; refusing automatic checklist or user assignment. "
            "Pass the real project album with --companycam-project-id, or create a new reviewed album.\n"
            f"{json.dumps(cc_match, indent=2)}"
        )
    return project


def apply_companycam_checklist(project_id: str, checklist_id: str, apply: bool, force_new: bool = False) -> dict[str, Any]:
    cmd = [
        "npm", "run", "dev", "--", "projects", "apply-checklist",
        project_id,
        "--checklist-template-id", checklist_id,
        "--json",
    ]
    if force_new:
        cmd.insert(-1, "--force-new")
    if not apply:
        cmd.insert(-1, "--dry-run")
    return parse_json(run(cmd, COMPANYCAM_REPO, companycam_env(writes=apply)))


def assign_companycam(project_id: str, user_id: str, apply: bool) -> dict[str, Any]:
    cmd = ["npm", "run", "dev", "--", "projects", "assign-user", project_id, "--user-id", user_id, "--json"]
    if not apply:
        cmd.insert(-1, "--dry-run")
    return parse_json(run(cmd, COMPANYCAM_REPO, companycam_env(writes=apply)))


def job_line(job: dict[str, Any]) -> str:
    client = job.get("client") or {}
    client_num = gid_number(str(client.get("id") or ""))
    job_num = gid_number(str(job.get("id") or ""))
    if client_num and job_num:
        return f"Job: <https://secure.getjobber.com/clients/{client_num}|{client.get('name')}> - <https://secure.getjobber.com/work_orders/{job_num}|Job #{job.get('jobNumber')}>"
    return f"Job: {client.get('name')} - Job #{job.get('jobNumber')}"


def slack_body(job: dict[str, Any], sub: str, sub_pay: float, sale: float, date_display: str, kind: str, note: str | None = None) -> str:
    margin = sale - sub_pay
    margin_pct = (margin / sale * 100) if sale else 0
    address = ((job.get("property") or {}).get("address") or {})
    lines = [
        job_line(job),
        f"Location: {display_location(address)}",
        f"Sub: {sub}",
        f"Type of Service: {job.get('title') or 'Service'} ({kind})",
        f"Date of Service: {date_display}",
        f"Sale: {money(sale)}",
        f"Sub Pay: {money(sub_pay)}",
        f"Margin: {money(margin)} / {margin_pct:.2f}%",
    ]
    if note:
        lines.append(f"Notes: {note}")
    return "\n".join(lines)


def slack_info_body(job: dict[str, Any], sub: str, date_display: str, note: str) -> str:
    address = ((job.get("property") or {}).get("address") or {})
    return "\n".join([
        job_line(job),
        f"Location: {display_location(address)}",
        f"Sub: {sub}",
        f"Type of Service: {job.get('title') or 'Service'}",
        f"Date of Service: {date_display}",
        f"Note: {note}",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run or apply KC PP job expense, CompanyCam, and Slack body prep.")
    parser.add_argument("job_number")
    parser.add_argument("--sub", required=True)
    parser.add_argument("--pay")
    parser.add_argument("--sale", help="Override sale amount for costing/Slack, useful for recurring visit pricing.")
    parser.add_argument("--date", required=True)
    parser.add_argument("--kind", default="One-Off")
    parser.add_argument("--job-info", action="store_true", help="Prepare an info-only Slack post and skip expense/margin.")
    parser.add_argument("--note", help="Slack note text. Required for info-only posts; optional for costing posts.")
    parser.add_argument("--reason", default=None)
    parser.add_argument("--companycam-project-id", help="Use an existing CompanyCam project instead of address sync/create.")
    parser.add_argument("--create-companycam-project", action="store_true", help="Allow creating a CompanyCam project when lookup finds no match.")
    parser.add_argument("--force-new-checklist", action="store_true", help="Create a fresh checklist instance even when the template already exists.")
    parser.add_argument("--companycam-user-id")
    parser.add_argument("--companycam-user-query")
    parser.add_argument("--checklist-template-id", default=None)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--skip-expense", action="store_true")
    parser.add_argument("--skip-companycam", action="store_true")
    args = parser.parse_args()

    if args.job_info:
        args.skip_expense = True
        if not args.note:
            parser.error("--job-info requires --note")
    elif args.pay is None:
        parser.error("--pay is required unless --job-info is set")

    if not args.checklist_template_id:
        args.checklist_template_id = default_checklist_for_kind(args.kind)

    iso_date, date_display = normalize_date(args.date)
    sub_pay = amount(args.pay)
    pp_assignment = match_pp_assignment(args.sub)
    slack_sub = str((pp_assignment or {}).get("slackSub") or args.sub)
    expense_vendor = str((pp_assignment or {}).get("expenseVendor") or args.sub)
    job = resolve_job(args.job_number)
    address = ((job.get("property") or {}).get("address") or {})
    quote = ((job.get("quote") or {}).get("amounts") or {})
    sale = amount(args.sale) if args.sale is not None else amount(quote.get("total") or job.get("total"))

    cc_users = resolve_companycam_users(args, pp_assignment)

    expense_action = "skipped" if args.skip_expense else "would-create"
    expense_result = None
    if not args.skip_expense:
        expenses = list_expenses(args.job_number)
        existing = matching_expense(expenses, expense_vendor, sub_pay, iso_date)
        expense_action = "skip-existing" if existing else "would-create"
        expense_result = existing
        if args.apply and not existing:
            expense_result = create_expense(args.job_number, expense_vendor, str(args.pay), date_display, args.reason or args.kind)
            expense_action = "created"

    cc_sync = None
    cc_assignment = []
    project_id = None
    jobber_companycam_project_id = companycam_project_id_from_job(job)
    if not args.skip_companycam:
        if args.companycam_project_id:
            project_id = str(args.companycam_project_id)
            cc_sync = apply_companycam_checklist(project_id, args.checklist_template_id, args.apply, args.force_new_checklist)
        elif jobber_companycam_project_id:
            project_id = str(jobber_companycam_project_id)
            checklist = apply_companycam_checklist(project_id, args.checklist_template_id, args.apply, args.force_new_checklist)
            cc_sync = {
                "command": "jobber customFields + projects apply-checklist",
                "action": "jobber-companycam-custom-field",
                "projectId": project_id,
                "checklist": checklist,
            }
        else:
            if not address:
                raise FlowError("Job has no address; cannot sync CompanyCam safely")
            cc_match = match_companycam(address)
            try:
                project = select_companycam_project_match(cc_match, address)
                project_id = str(project.get("id") or "")
                checklist = apply_companycam_checklist(project_id, args.checklist_template_id, args.apply, args.force_new_checklist)
                cc_sync = {
                    "command": "projects match+apply-checklist",
                    "action": "matched-existing-project",
                    "match": cc_match,
                    "project": project,
                    "checklist": checklist,
                }
            except FlowError:
                safe_no_match = (
                    cc_match.get("status") == "none"
                    and not (cc_match.get("matches") or [])
                    and cc_match.get("candidates", 0) < COMPANYCAM_PROJECT_SEARCH_PAGE_SIZE
                )
                if args.create_companycam_project and safe_no_match:
                    cc_sync = sync_companycam(
                        args.job_number,
                        f"{(job.get('client') or {}).get('name')} - {job.get('title')}",
                        address,
                        args.checklist_template_id,
                        args.apply,
                    )
                    project = cc_sync.get("project") or (cc_sync.get("plan") or {}).get("project")
                    project_id = str((project or {}).get("id") or "")
                else:
                    raise
        if project_id:
            for cc_user in cc_users:
                cc_assignment.append(assign_companycam(project_id, str(cc_user["id"]), args.apply))

    margin = sale - sub_pay
    costing = None if args.job_info else {
        "sale": sale,
        "subPay": sub_pay,
        "margin": margin,
        "marginPercent": (margin / sale * 100) if sale else None,
    }
    body = (
        slack_info_body(job, slack_sub, date_display, str(args.note))
        if args.job_info
        else slack_body(job, slack_sub, sub_pay, sale, date_display, args.kind, args.note)
    )
    out = {
        "ok": True,
        "mode": "apply" if args.apply else "dry-run",
        "job": {
            "id": job.get("id"),
            "jobNumber": job.get("jobNumber"),
            "client": (job.get("client") or {}).get("name"),
            "title": job.get("title"),
            "status": job.get("jobStatus"),
            "location": display_location(address),
            "quote": quote,
        },
        "ppAssignment": {
            "inputSub": args.sub,
            "matchedKey": (pp_assignment or {}).get("key"),
            "slackSub": slack_sub,
            "expenseVendor": expense_vendor,
        },
        "expense": {"action": expense_action, "vendor": expense_vendor, "result": expense_result},
        "companyCam": {
            "assignmentPolicy": "strict-registry-or-explicit-id; explicit query is dry-run discovery only",
            "projectPolicy": "explicit-id-or-jobber-companycam-custom-field-or-safe-single-address-match; no new project without explicit create intent",
            "jobberCustomFieldProjectId": jobber_companycam_project_id,
            "users": cc_users,
            "sync": cc_sync,
            "assignments": cc_assignment,
        },
        "costing": costing,
        "slack": {
            "channelId": DEFAULT_SLACK_CHANNEL_ID,
            "channelName": DEFAULT_SLACK_CHANNEL_NAME,
            "delivery": "not-sent-by-script",
            "body": body,
        },
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FlowError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(1)
