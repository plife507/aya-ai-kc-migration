# Jobber job identity notes

## Proven local example

Resolved Job #20371 to:

- GraphQL id: `Z2lkOi8vSm9iYmVyL0pvYi8xNDE3NTQwMTk=`
- decoded id: `gid://Jobber/Job/141754019`
- browser URL id: `141754019`
- direct URL: `https://secure.getjobber.com/jobs/141754019`
- title: `Hardscape cleaning - FLEX TIME`
- client: `Joe  Cardenas`
- status: `today`

## Identity model

For Jobber job work, keep these distinct:

- `jobNumber`: human-facing job number
- GraphQL `id`: encoded API identifier
- browser URL id: final numeric segment inside the decoded GraphQL id
- direct URL: `https://secure.getjobber.com/jobs/<browser-url-id>`

These values are connected but should not be treated as interchangeable.

## Local tool path

Active primary CLI:

`/home/plife507/Projects/jobber/jobber-cli-v3`

Typical lookup command:

```bash
cd /home/plife507/Projects/jobber/jobber-cli-v3
JOBBER_ENV_PATH=/home/plife507/Projects/jobber/.env \
JOBBER_OAUTH_SKIP_AUTHORIZE=1 \
yarn dev search jobs 20371 --json
```

Deprecated legacy CLI path, do not use for current work:

`/home/plife507/Projects/KC/jobber-cli`

## Base skill purpose

This skill exists to resolve the canonical identity bundle first so later Jobber actions can use the right job record.

## Failure mode to remember

The main failure mode seen so far was stale Jobber OAuth, not missing schema support.

## Proven accounting code mapping

From the live authenticated Jobber expense edit modal in the attached `user` browser lane:

- field name: `expense[accounting_code_id]`
- human label: `subcontractors`
- internal value / `accountingCodeId`: `111162`

Additional confirmed live dropdown mappings:

- `commissions/marketing costs` -> `124659`
- `equipment rental` -> `37069`
- `fuel expense` -> `37024`
- `lodging` -> `37070`
- `permits/licenses` -> `37071`
- `supplies and materials` -> `37021`

Full captured map lives here:

- `/home/plife507/AYA-CLAW/skills/jobber-job-identity/references/accounting-codes.md`
- `/home/plife507/AYA-CLAW/skills/jobber-job-identity/references/accounting-codes.json`

Reusable local lookup helper:

- `/home/plife507/AYA-CLAW/scripts/jobber-accounting-code-lookup.py`

Examples:

```bash
/home/plife507/AYA-CLAW/scripts/jobber-accounting-code-lookup.py subcontractors
/home/plife507/AYA-CLAW/scripts/jobber-accounting-code-lookup.py "powdered degreaser"
```
