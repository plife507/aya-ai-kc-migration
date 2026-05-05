---
name: jobber-job-identity
description: Resolve a Jobber job number into the canonical job identity needed for follow-on actions. Use the active TypeScript Jobber CLI at /home/plife507/Projects/jobber/jobber-cli-v3. Older KC jobber-cli examples are deprecated and should not be used for current work.
---

# Jobber Job Identity

Use this skill when the first step is: visible Jobber job number -> exact Jobber job record.

This is a base skill for later actions.

Once the job is resolved correctly, other workflows can build on it, for example:

- open the job in the browser
- inspect notes, invoices, expenses, or visits
- map a job to other systems
- perform API lookups or later controlled writes

## Goal

Turn a visible Jobber job number like `20371` into a stable identity bundle:

- `jobNumber`
- GraphQL job `id`
- browser URL id
- direct secure Jobber URL
- title
- client name
- job status

Example bundle:

- job number: `20371`
- GraphQL id: `Z2lkOi8vSm9iYmVyL0pvYi8xNDE3NTQwMTk=`
- decoded id: `gid://Jobber/Job/141754019`
- browser URL id: `141754019`
- URL: `https://secure.getjobber.com/jobs/141754019`

## Core rules

- Do not guess the browser URL id from the job number.
- Do not assume the first search result is the right one without checking `jobNumber`.
- Resolve the job identity first before taking other job-specific actions.
- When a known downstream path already exists, use the resolved identity to stay on that path instead of improvising a new route.
- If identity resolution is ambiguous or auth-blocked, surface the blocker as an investigation item: blocker, known results, missing proof, risk, and next verification.

The visible job number, GraphQL id, and browser URL id are related but not interchangeable.

## Preferred path

Use the active TypeScript Jobber CLI/API first:

```bash
cd /home/plife507/Projects/jobber/jobber-cli-v3
JOBBER_ENV_PATH=/home/plife507/Projects/jobber/.env \
JOBBER_OAUTH_SKIP_AUTHORIZE=1 \
yarn dev search jobs 20371 --json
```

This should return items including:

- `id`
- `jobNumber`
- `title`
- `jobStatus`
- `client.name`

Do not use old KC-path examples for current work.

## Resolution workflow

### 1. Search by job number

Run Jobber search using the visible job number as the search term.

### 2. Match exactly

From the returned items, choose the row whose `jobNumber` exactly matches the requested job number.

If multiple results exist, do not guess. Identify the exact one by:

- `jobNumber`
- title
- client name
- status

### 3. Read the GraphQL id

Example:

```text
Z2lkOi8vSm9iYmVyL0pvYi8xNDE3NTQwMTk=
```

### 4. Decode the GraphQL id

The id is base64 for a string shaped like:

```text
gid://Jobber/Job/141754019
```

The final numeric segment is the browser URL id.

### 5. Build the direct browser URL

```text
https://secure.getjobber.com/jobs/<browser-url-id>
```

Example:

```text
https://secure.getjobber.com/jobs/141754019
```

## Minimal extraction pattern

```bash
python3 - <<'PY'
import base64
s = 'Z2lkOi8vSm9iYmVyL0pvYi8xNDE3NTQwMTk='
print(base64.b64decode(s).decode())
PY
```

Then take the final path segment.

## Output bundle

When resolving a job, return a compact identity bundle:

- Job #
- title
- client
- status
- GraphQL id
- browser URL id
- direct URL

That bundle is the base object for follow-on work.

If resolution is incomplete, do not return a fake bundle. Return `Status: blocked` or `Status: needs verification` with the exact blocker and next check.

## Follow-on action rule

After identity is resolved, later tasks should use the resolved job identity rather than re-guessing from partial browser context.

Examples of follow-on actions that should start from the resolved identity bundle:

- open this job
- check expenses for this job
- inspect notes on this job
- pull invoices for this job
- compare this job to another system record

## Auth notes

If the CLI fails with expired token or OAuth refresh errors:

- re-authorize Jobber OAuth first
- then rerun the search

Do not claim the lookup is impossible when the schema supports it. Usually the blocker is auth, not capability.

## Reference

Read `/home/plife507/AYA-CLAW/skills/jobber-cli-v3-operator/SKILL.md` when the broader task is operating the active TS Jobber CLI rather than only resolving one job.

Read `/home/plife507/AYA-CLAW/skills/jobber-job-identity/references/notes.md` when you need the proven local example or the distinction between job number, GraphQL id, and browser URL id.

Read `/home/plife507/AYA-CLAW/skills/jobber-job-identity/references/accounting-codes.md` when a Jobber expense workflow needs a known `accountingCodeId` for subcontractors, supplies, materials, labor, or other mapped cost labels.

Use `/home/plife507/AYA-CLAW/skills/jobber-job-identity/references/accounting-codes.json` for machine-readable label -> `accountingCodeId` lookup.
