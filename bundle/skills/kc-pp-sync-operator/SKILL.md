---
name: kc-pp-sync-operator
description: Operate, inspect, and safely update the KC Power Clean Google Sheets sync system and its spreadsheet outputs. Use when working with the KC PP Sync sheet, Dashboard, ⚡ Command, Log, month tabs, recurring tabs, GTP tabs, or the kc-pp-sync Cloud Run and Scheduler setup. Also use when reading or validating sync results, tracing how sheet data is structured, deciding whether a problem lives in Sheets vs sync logic vs runtime, triggering manual syncs, or checking deploy/runtime state without guessing business rules.
---

# KC PP Sync Operator

Use this skill to work safely with the KC Power Clean spreadsheet and its sync service.

## Core rules

- Default to read-only inspection unless Nathan explicitly asks for edits.
- Do not guess tab meaning from tab names alone when the sheet contents or repo docs can be read directly.
- Distinguish between a manual sheet correction and a sync-generated symptom before editing anything.
- Prefer `gog sheets` for spreadsheet reads and small precise edits.
- Prefer `gcloud` for Cloud Run, Scheduler, Secret Manager, IAM, and logs.
- Do not expose secrets, copied credential values, raw tokens, or Secret Manager contents in chat.
- When a requested fix looks like it belongs in sync logic rather than the sheet, say so.

## System map

Primary surfaces:
- **Spreadsheet**: KC PP Sync sheet
- **Runtime**: Cloud Run service `kc-pp-sync`
- **Triggers**: Cloud Scheduler jobs
- **Sources**: Jobber GraphQL + HeyPros GraphQL

Read these references when needed:
- `references/sheet-architecture.md` for tab families, layout differences, and margin behavior
- `references/runtime-operations.md` for Cloud Run, Scheduler, deploy, and manual sync flows
- `references/business-cautions.md` for matching/data-shape cautions and approved posture

## Decide the lane first

Choose the right surface before acting:

- **Spreadsheet lane**: tab layout, formulas, values, dashboard outputs, command/log inspection, safe manual edits
- **Runtime lane**: Cloud Run service state, revisions, scheduler jobs, runtime identity, logs, manual sync triggers
- **Business-rule lane**: what a tab means, how matching works, whether a sheet symptom is expected output or a real defect

If business meaning is unclear, read the relevant reference file and the repo docs before making claims.
If the broader KC request also involves Slack posting, Jobber writes, or costing decisions, read `/home/plife507/AYA-CLAW/references/topic-kc.md` and keep sheet/runtime diagnosis separate from those downstream actions.

## Spreadsheet workflow

For sheet work:

1. Identify the exact spreadsheet and tab.
2. Read metadata or headers before reasoning from values.
3. If precision matters, inspect the header row plus nearby example rows.
4. If formulas or formatting matter, inspect them instead of inferring from appearance.
5. Keep edits minimal and targeted.

Typical spreadsheet tasks:
- inspect current month, previous month, or recurring tabs
- compare recurring vs one-off layout
- inspect Dashboard outputs
- inspect ⚡ Command / Log for sync evidence
- validate whether a result looks generated correctly
- make a narrow manual correction when explicitly requested

## Runtime workflow

For runtime work, inspect in this order:

1. Cloud Run service details
2. scheduler jobs and schedules
3. runtime service account / invocation path
4. recent logs and latest ready revision
5. repo docs or code only if runtime behavior still needs explanation

Typical runtime tasks:
- confirm the service is healthy
- confirm which scheduler jobs exist and what they run
- inspect recent revisions and logs after a suspected failure
- trigger a manual sync safely
- confirm whether a sheet symptom likely came from the runtime

## Manual sync posture

There are two normal manual-sync lanes:
- in-sheet Apps Script menu (`KC Sync`)
- direct authenticated Cloud Run POST

Use repo/runtime facts before invoking anything. Prefer narrow mode/tab targeting over broad runs when investigating. For exact payloads, current source-tab map, scheduler mode map, and verification commands, read `/home/plife507/AYA-CLAW/skills/kc-pp-sync/references/manual-sync.md`.

If Nathan asks to sync an exact month tab, treat that as a direct runtime task, not a spreadsheet-edit task.

Default interpretation examples:
- "sync April" -> trigger the one-off `April` tab sync
- "sync April - R" -> trigger the recurring `April - R` tab sync
- "sync the April tab on the KC PP sheet" -> trigger a direct authenticated Cloud Run POST with `{"tab":"April"}`

For exact-tab sync requests, keep the flow tight:
1. confirm the target tab name if ambiguous
2. read the manual sync runbook for exact tab and mode rules
3. use the direct API lane with exact `tab` targeting
4. verify success from the API response or Cloud Run logs
5. report the result briefly, including row/update evidence when available

Do not drift into broad service inspection or unrelated sheet reads unless the sync fails or the target is unclear.

## Write-request rule

Before any sheet write or runtime-affecting action:
- confirm the exact target tab/range or runtime surface
- decide whether the issue is a one-off correction or should be fixed in code/runtime
- say when the requested manual fix appears to be masking a generated problem

## Common commands

### Read spreadsheet metadata

```bash
gog sheets metadata <spreadsheet-id> --json
```

### Read a sheet range

```bash
gog sheets get <spreadsheet-id> '<tab>!A1:Z20' --plain
```

### Inspect sheet notes or links

```bash
gog sheets notes <spreadsheet-id> '<tab>!A1:Z20'
gog sheets links <spreadsheet-id> '<tab>!A1:Z20'
```

### Inspect Cloud Run

```bash
gcloud run services describe kc-pp-sync --region us-central1 --project aya-gservicies
gcloud scheduler jobs list --location us-central1 --project aya-gservicies
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="kc-pp-sync"' --project aya-gservicies --limit 20
```

## Output style

Keep replies practical:
- say what you inspected
- separate observed facts from interpretation
- call out uncertainty instead of guessing
- for edits, state exactly what changed or would change
- when the root cause likely lives in sync logic or runtime, say that directly
- use Executive KC mode for Nathan-facing summaries: professional, polished, concise, helpful, and firm on closure
- if blocked, report blocker, known facts, missing facts, risk, and next verification
