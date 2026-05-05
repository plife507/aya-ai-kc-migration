---
name: kc-pp-sync
description: Trigger and verify KC Power Clean PP sheet sync runs for exact month tabs, recurring tabs, dashboard refreshes, or narrow manual sync requests. Use when Nathan says things like "sync April", "sync March - R", "sync the May tab on the KC PP sheet", "refresh Dashboard", or otherwise wants the kc-pp-sync runtime to run a specific targeted sync without broad investigation.
---

# KC PP Sync

Use this skill for direct KC PP sync requests.

This skill is for running a targeted sync and confirming the result.
It is not the broad troubleshooting skill. For architecture/debug/runtime diagnosis beyond the sync itself, use `kc-pp-sync-operator`.

## Core rule

When Nathan asks to sync a specific KC PP tab, default to the narrowest runtime action that matches the request.

Do not drift into broad sheet inspection, unrelated runtime checks, or document hunting unless:
- the target tab is unclear
- the sync call fails
- verification is ambiguous

## Default interpretations

Treat month names as variable, not April-specific.

- `sync <Month>` -> one-off tab `<Month>`
- `sync <Month> - R` -> recurring tab `<Month> - R` when that exact tab exists; otherwise read metadata before choosing the tab name
- `sync the <Month> tab on the KC PP sheet` -> exact tab `<Month>`
- `refresh dashboard` or `sync dashboard` -> dashboard refresh path

Examples:
- `sync March` -> `March`
- `sync March - R` -> `March - R`
- `sync the May tab on the KC PP sheet` -> `May`

If the request names an exact tab, prefer exact `tab` targeting over generic mode targeting. Current recurring month tabs use full month names such as `February - R`; if a shorthand appears in a request, read metadata before choosing an exact tab.

## Execution flow

1. Confirm the target only if ambiguous.
2. Read `references/manual-sync.md` for exact-tab and mode rules.
3. Use the direct authenticated Cloud Run POST lane.
4. Prefer exact JSON payloads:
   - `{"tab":"<Month>"}`
   - `{"tab":"<Month> - R"}` when that exact tab exists
   - `{"mode":"dashboard"}`
5. Verify success from:
   - API response first, if it returns clearly
   - Cloud Run logs second, if the request backgrounds or the response is incomplete
6. Reply briefly with the result and any concrete update evidence available.

## Manual sync runbook

Read `references/manual-sync.md` before running or documenting manual syncs. It contains the exact Cloud Run POST pattern, current source-tab map, scheduler mode map, and verification commands.

Read `references/runtime.md` only when you need the shorter runtime identity/curl reference.

## Output style

Keep the reply short and operational:
- confirm the target synced
- say if it completed cleanly
- include row/update evidence when available
- if verification is partial, say exactly what is confirmed vs not confirmed

## Boundaries

- Do not treat this as a spreadsheet edit request.
- Do not make manual sheet edits just because a sync was requested.
- If the sync fails twice or the target is unclear, stop and surface the blocker cleanly.
