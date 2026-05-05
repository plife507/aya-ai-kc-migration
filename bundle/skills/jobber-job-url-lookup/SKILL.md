---
name: jobber-job-url-lookup
description: Get a direct Jobber job URL from a Jobber job number using the active TypeScript Jobber CLI at /home/plife507/Projects/jobber/jobber-cli-v3. Older KC jobber-cli examples are deprecated and should not be used for current work.
---

# Jobber Job URL Lookup

Use this skill when the task is specifically: job number -> direct Jobber job URL.

## Goal

Turn a visible Jobber job number like `20371` into:

- the GraphQL job id
- the browser URL id
- the direct secure Jobber link

Example:

- job number: `20371`
- GraphQL id: `Z2lkOi8vSm9iYmVyL0pvYi8xNDE3NTQwMTk=`
- browser URL id: `141754019`
- URL: `https://secure.getjobber.com/jobs/141754019`

## Core rule

Do not guess the browser URL id from the job number.

The browser URL id is not the same thing as the visible Jobber job number. Look it up through the API, then extract it from the GraphQL id.

## Preferred path

Use the active TypeScript Jobber CLI first:

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

## How to build the URL

### 1. Find the matching item

From the API/CLI response, select the item whose `jobNumber` exactly matches the requested job number.

### 2. Read the GraphQL id

Example:

```text
Z2lkOi8vSm9iYmVyL0pvYi8xNDE3NTQwMTk=
```

### 3. Decode the GraphQL id

The id is base64 for a string shaped like:

```text
gid://Jobber/Job/141754019
```

The final numeric segment is the browser URL id.

### 4. Build the direct link

```text
https://secure.getjobber.com/jobs/<browser-url-id>
```

Example:

```text
https://secure.getjobber.com/jobs/141754019
```

## One-line extraction pattern

```bash
python3 - <<'PY'
import base64
s = 'Z2lkOi8vSm9iYmVyL0pvYi8xNDE3NTQwMTk='
print(base64.b64decode(s).decode())
PY
```

Then take the final path segment.

## Workflow

1. Run Jobber search for the job number.
2. Confirm the returned `jobNumber` matches exactly.
3. Read the GraphQL `id`.
4. Decode it if needed.
5. Extract the final numeric segment.
6. Return the direct secure Jobber URL.

## Auth notes

If the CLI fails with expired token or OAuth refresh errors:

- re-authorize Jobber OAuth first
- then rerun the search

Do not claim the lookup is impossible when the schema supports it. Usually the blocker is auth, not capability.

## Output style

Keep the result compact:

- Job #
- GraphQL id
- browser URL id
- direct URL

If multiple matches are returned, call that out and identify the exact match by `jobNumber`, title, and client.

## Direction note

This skill is a narrow helper under the active TS runtime. For broader Jobber CLI operation, use `/home/plife507/AYA-CLAW/skills/jobber-cli-v3-operator/SKILL.md`.
