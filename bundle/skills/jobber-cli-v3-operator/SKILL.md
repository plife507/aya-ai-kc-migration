---
name: jobber-cli-v3-operator
description: Operate the active TypeScript Jobber CLI v3 at /home/plife507/Projects/jobber/jobber-cli-v3 for all Jobber API read/write work, headless automation, token-aware scripting, schema-aware queries, and note/expense helpers. This supersedes deprecated original Jobber CLI guidance and is the default canonical Jobber CLI skill.
---

# Jobber CLI v3 Operator

Use this skill for the active Jobber CLI v3 runtime. This is the replacement for deprecated original Jobber CLI guidance.

The current source of truth is:

- repo: `/home/plife507/Projects/jobber/jobber-cli-v3`
- workspace root: `/home/plife507/Projects/jobber`
- shared env: `/home/plife507/Projects/jobber/.env`
- shared token cache: `/home/plife507/Projects/jobber/tokens/jobber_tokens.json`
- OAuth manager: `/home/plife507/Projects/jobber/oauth/jobber_oauth_manager.py`

Do not use the older KC JS CLI path for normal work. The v3.0 TypeScript repo is the canonical runtime.

## Core direction

- Treat `jobber-cli-v3` as the only default CLI.
- Treat old KC `jobber-cli` guidance as deprecated.
- Use v3 command patterns, docs, and repo layout when writing instructions, wrappers, or automations.
- Prefer known wrappers/helpers over ad hoc mutation discovery when a stable path already exists.
- Keep writes gated per-call with `JOBBER_WRITES_ENABLED=1` only where needed.
- Use explicit env on every invocation.
- Prefer structured JSON output over human-readable output.
- For KC execution, report in Executive KC mode: concise result, truthful status, evidence from Jobber, and the next action or blocker.

## Decision rule

Use this skill when the task is any of these:

- run or inspect the active Jobber CLI
- create or update Jobber helper scripts or wrappers
- perform Jobber search, get, query, schema, doctor, notes, job-note, or job-expense work through v3
- adapt automation to the TS CLI
- reason about headless or agent-safe Jobber usage
- update Aya's Jobber operating guidance to point at v3.0

If older KC-path material appears, treat it as deprecated reference material and move the task back onto v3.0 unless Nathan explicitly asks for archaeology or cleanup.
If the KC request also involves Slack delivery, thread binding, PP costing, or PP sheet interpretation, read `/home/plife507/AYA-CLAW/references/topic-kc.md` and keep the lane split explicit instead of letting the Jobber step absorb the whole task.

## Canonical invocation pattern

For headless and agent-safe use, run commands like this:

```bash
cd /home/plife507/Projects/jobber/jobber-cli-v3
JOBBER_ENV_PATH=/home/plife507/Projects/jobber/.env \
JOBBER_OAUTH_SKIP_AUTHORIZE=1 \
yarn dev <command> [args...] --json
```

For writes, add the writes gate inline only for that one call:

```bash
cd /home/plife507/Projects/jobber/jobber-cli-v3
JOBBER_WRITES_ENABLED=1 \
JOBBER_ENV_PATH=/home/plife507/Projects/jobber/.env \
JOBBER_OAUTH_SKIP_AUTHORIZE=1 \
yarn dev job-note create 12241 --message "hi" --json
```

## Core safety rules

- Never rely on ambient cwd or env.
- Always set `JOBBER_ENV_PATH` explicitly.
- Always set `JOBBER_OAUTH_SKIP_AUTHORIZE=1` in headless/agent mode.
- Always prefer `--json` for machine-readable output.
- Never export `JOBBER_WRITES_ENABLED` globally.
- Check exit code before parsing stdout.
- Capture stdout and stderr separately in wrappers.
- Do not add tight retry loops on top of the CLI's internal retry/backoff behavior.

## Exit code map

Use this branching model:

- `0` success
- `2` validation error
- `3` auth failure
- `4` rate limit / throttle
- `5` not found
- `6` config error
- `7` non-interactive block
- `10` internal, including writes-disabled refusal

Practical handling:

- exit `3`: refresh token or escalate for browser-side re-authorize
- exit `4`: wait generously before retrying
- exit `5`: verify the id type and lookup path
- exit `10` with writes-disabled message: do not bypass, treat it as a human decision gate

## Active command surface

The shipped v3 surface includes:

- `status`
- `token check`
- `token oauth-refresh`
- `token oauth-authorize`
- `get`
- `query`
- `search`
- `notes`
- `schema fetch|analyze|help`
- `doctor`
- `job-note list|create|edit|delete`
- `job-expense list|create|edit|delete`

These v3 commands are the canonical command surface for documenting and implementing workflows.

## Job resolution rule

For job-number lookup work, search first and match exact `jobNumber`.
Do not guess the encoded Jobber id from the visible job number.

Typical path:

```bash
cd /home/plife507/Projects/jobber/jobber-cli-v3
JOBBER_ENV_PATH=/home/plife507/Projects/jobber/.env \
JOBBER_OAUTH_SKIP_AUTHORIZE=1 \
yarn dev search jobs 12241 --json
```

Then select the exact result and use its encoded id for follow-on operations.

## Mutation posture

For note and expense mutations:

- use v3 `job-note` and `job-expense`
- keep writes gated inline per command
- design batch work for undo
- journal created ids before the next mutation in a sequence
- do not run parallel mutations against the same account

Before any live Jobber write, do a quick mutation preflight:

- exact target record
- create vs edit vs delete
- record id if editing or deleting
- safe quoting for freeform text
- canonical command path or wrapper

If a stable wrapper exists, use it instead of composing raw mutation flags from scratch.
Do not drift into mid-execution help or syntax fishing on a live KC task unless genuinely blocked.
If the path is still unclear after a quick check, stop and ask Nathan rather than improvising a new route.

When blocked, use the investigation shape:
- blocker
- known Jobber/job/command facts
- missing authorization, id, field, or command proof
- risk of guessing
- next verification

## Unassigned / unscheduled visit audit

To find Jobber visits that need assignment review after tech changes or deactivation, use the read-only wrapper:

```bash
python3 /home/plife507/AYA-CLAW/skills/jobber-cli-v3-operator/scripts/find_unassigned_visits.py --days 365
```

Default behavior scans scheduled visits from today through the next 365 days and separately scans `status=UNSCHEDULED` visits. It flags visits with no operational assignee after ignoring `HQ - ...` sales/admin users. Use `--strict-empty` when you only want visits with zero assigned users, `--job-numbers-only` for a compact list, `--no-unscheduled` to skip unscheduled visits, and `--from YYYY-MM-DD --days N` or `--to YYYY-MM-DD` for a custom range. Use `--day-by-day --output-json <path>` when a full-year range query throttles; the JSON payload includes `scheduled.jobNumbersByDay`, which lists each job number only once per date.

## Subcontractor expense hard path

For subcontractor expense creation, do not compose raw `job-expense create` fields freehand.
Use the deterministic wrapper:

```bash
python3 /home/plife507/AYA-CLAW/skills/jobber-cli-v3-operator/scripts/create_subcontractor_expense.py \
  <jobNumber> \
  --vendor "Beto" \
  --amount 150 \
  --date 4/19/2026 \
  --reason "Mobilization due police stop ordinance violation"
```

This wrapper fixes the field mapping to:

- `title = Sub`
- `description = vendor plus useful qualifier`
- `total = <amount>`
- `date = <ISO-normalized date>`
- `accountingCodeId = MTExMTYy` (`subcontractors`)

Date normalization hard rule:
- date-only inputs must normalize to midday UTC (`T12:00:00Z`), not midnight UTC
- reason: midnight UTC can render as the previous calendar day in Pacific time and make Jobber expenses appear one day early

Description posture:

- vendor name should live in description
- reason may live in description
- amount may also appear in description if useful
- the flexible field is description, not title or accounting code

Use this wrapper whenever the requested expense is subcontractor labor/cost.
Only fall back to raw `job-expense create` when the expense is clearly not a subcontractor expense.

This is the first enforced expense profile, not the last one.
Prepare future expense types by adding new fixed profiles with their own:

- title matcher
- fixed title
- accounting code id
- optional vendor/name extraction rule

## Slack write intent hard rules

When operating from Slack or any Slack-derived thread summary, do not guess between note and expense workflows.

Route by explicit user intent:

- if the user says `write a note`, `add a note`, `job note`, or asks to log customer/job context, use only `job-note`
- if the user says `expense`, `cost`, `charge`, `subcontractor`, `material`, or asks to add/edit/remove a job cost, use only `job-expense`

Never silently convert a note request into an expense mutation.
Never silently convert an expense request into a note mutation.

For `job-note`:

- required: `jobNumberOrId`
- required: `message`
- optional: `pinned`
- do not invent structured accounting fields

For `job-expense`:

- required: `jobNumberOrId`
- required: `title`
- required: `date`
- optional but usually required in practice: `total`
- optional: `description`
- optional: `accountingCodeId`

When the user gives a plain date like `4/20` or `2026-04-20`, preserve the intended local calendar day by using the date-normalization rule above rather than raw midnight UTC.

For KC PP correction requests like `add expense but don't calculate P&L`, create or update only the requested Jobber expense. Do not compute margin, do not convert an info-only Slack post into a costing post, and route any Slack note edit through the KC Slack channel operator.

If the request is ambiguous, stop and ask a short clarification question.
Examples:

- `Do you want this added as a Jobber note or as a job expense?`
- `If this is an expense, I need title, date, and amount.`

## References

Read these when needed:

- `/home/plife507/Projects/jobber/jobber-cli-v3/README.md`
- `/home/plife507/Projects/jobber/jobber-cli-v3/docs/agent-usage.md`
- `/home/plife507/Projects/jobber/jobber-cli-v3/docs/headless-usage.md`
- `/home/plife507/Projects/jobber/jobber-cli-v3/TODO.md`

For durable Jobber accounting-code mappings already captured from the live UI, also read:

- `/home/plife507/AYA-CLAW/skills/jobber-job-identity/references/accounting-codes.md`
- `/home/plife507/AYA-CLAW/skills/jobber-job-identity/references/accounting-codes.json`

## Deprecated path

Old local guidance pointed at `/home/plife507/Projects/KC/jobber-cli`.
That path is deprecated and should not be used for current Jobber operations.

When updating docs or instructions:

- use `Projects/jobber/jobber-cli-v3`
- use `yarn dev` or `yarn node bin/jobber.js`
- use the shared `Projects/jobber/.env` + `tokens/` + `oauth/` layout
- rewrite or retire old KC-path examples instead of carrying them forward
