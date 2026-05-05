#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

JOBBER_REPO = "/home/plife507/Projects/jobber/jobber-cli-v3"
JOBBER_ENV_PATH = "/home/plife507/Projects/jobber/.env"
SUBCONTRACTOR_ACCOUNTING_CODE_ID = "MTExMTYy"
FIXED_TITLE = "Sub"


def normalize_date(value: str) -> str:
    candidates = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%Y/%m/%d",
    ]
    for pattern in candidates:
        try:
            return datetime.strptime(value.strip(), pattern).strftime("%Y-%m-%dT12:00:00Z")
        except ValueError:
            pass
    raise SystemExit(f"Unsupported date format: {value!r}")


def normalize_amount(value: str) -> str:
    cleaned = value.strip().replace("$", "").replace(",", "")
    amount = float(cleaned)
    if amount <= 0:
        raise SystemExit("Amount must be positive")
    return f"{amount:.2f}".rstrip("0").rstrip(".")


def build_description(vendor: str, reason: str) -> str:
    vendor = " ".join(vendor.strip().split())
    reason = " ".join(reason.strip().split())
    if not vendor:
        raise SystemExit("Vendor is required")
    if not reason:
        return vendor
    return f"{vendor} - {reason}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Jobber subcontractor expense with fixed field mapping.")
    parser.add_argument("job_number")
    parser.add_argument("--vendor", required=True)
    parser.add_argument("--amount", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    iso_date = normalize_date(args.date)
    total = normalize_amount(args.amount)
    description = build_description(args.vendor, args.reason)

    cmd = [
        "yarn",
        "dev",
        "job-expense",
        "create",
        args.job_number,
        "--title",
        FIXED_TITLE,
        "--date",
        iso_date,
        "--total",
        total,
        "--description",
        description,
        "--accounting-code-id",
        SUBCONTRACTOR_ACCOUNTING_CODE_ID,
        "--json",
    ]

    payload = {
        "jobNumber": args.job_number,
        "title": FIXED_TITLE,
        "date": iso_date,
        "total": total,
        "description": description,
        "accountingCodeId": SUBCONTRACTOR_ACCOUNTING_CODE_ID,
        "command": cmd,
    }

    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return 0

    env = os.environ.copy()
    env["JOBBER_WRITES_ENABLED"] = "1"
    env["JOBBER_ENV_PATH"] = JOBBER_ENV_PATH
    env["JOBBER_OAUTH_SKIP_AUTHORIZE"] = "1"

    proc = subprocess.run(
        cmd,
        cwd=JOBBER_REPO,
        env=env,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        if proc.stderr:
            sys.stderr.write(proc.stderr)
        if proc.stdout:
            sys.stderr.write(proc.stdout)
        return proc.returncode

    stdout = proc.stdout.strip()
    if stdout:
        print(stdout)
    else:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
