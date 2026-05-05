# KC PP Sync Manual Sync Runbook

Use this when Nathan asks for a manual `kc-pp-sync` run, an exact tab sync, or how the scheduled sync lanes work.

## Runtime

- Project: `aya-gservicies`
- Region: `us-central1`
- Cloud Run service: `kc-pp-sync`
- Service URL: `https://kc-pp-sync-823212137840.us-central1.run.app`
- Spreadsheet: `1p4lxIUjWFYNDp6ptqSMwyRcdle5Hcv5UMC6TdpZE99Q`
- Local repo: `/home/plife507/Projects/kc-pp-sync`

Manual syncs are HTTP POSTs to Cloud Run with a `gcloud auth print-identity-token` bearer token. Do not use `gcloud run jobs execute`; this is a Cloud Run service, not a Cloud Run Job.

## Direct API Pattern

```bash
TOKEN=$(gcloud auth print-identity-token)
curl -sS -X POST https://kc-pp-sync-823212137840.us-central1.run.app \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tab":"April - R"}'
```

For exact-tab requests, use the tab name exactly as it appears in Sheets. If the user gives a month shorthand and the live tab list is uncertain, read metadata first:

```bash
gog sheets metadata 1p4lxIUjWFYNDp6ptqSMwyRcdle5Hcv5UMC6TdpZE99Q --json | jq -r '.sheets[].properties.title'
```

## Exact Tab Syncs

Use `{"tab":"<exact tab>"}` for human-in-loop manual runs.

Current syncable source tabs observed on 2026-04-28:

| Tab | Payload | Notes |
|---|---|---|
| `January 2026` | `{"tab":"January 2026"}` | Legacy one-off. Exact only; the older-month mode intentionally excludes January. |
| `February` | `{"tab":"February"}` | Legacy one-off. |
| `February - R` | `{"tab":"February - R"}` | Full recurring February tab name. Former `Feb - R` abbreviation was renamed on 2026-04-28. |
| `March` | `{"tab":"March"}` | New one-off. |
| `March - R` | `{"tab":"March - R"}` | Recurring. |
| `April` | `{"tab":"April"}` | New one-off. |
| `April - R` | `{"tab":"April - R"}` | Recurring. |
| `May` through `December` | `{"tab":"May"}` etc. | New one-off tabs exist. Recurring tabs may not exist yet; check metadata before using `- R`. |

Do not directly sync generated/system tabs:
- `Dashboard`: use `{"mode":"dashboard"}` or `{"refreshDashboard":true}`
- `* - GTP $`: sync the source month tab instead
- `Log` and `KC Command`: operational surfaces, not source tabs

## Mode Syncs

Use `{"mode":"..."}` when Nathan asks for the service's normal scheduled lane rather than a named tab.

| Mode | Resolves to | Scheduler job | Schedule |
|---|---|---|---|
| `current` | current LA month one-off, e.g. `April` | `kc-pp-sync-hourly` | `*/20 * * * *` UTC |
| `current-r` | current LA month recurring, e.g. `April - R` | `kc-pp-sync-recurring` | `5,25,45 * * * *` UTC |
| `prev` | previous LA month one-off, e.g. `March` | `kc-pp-sync-prev-month` | `10,30,50 * * * *` UTC |
| `prev-r` | previous LA month recurring, e.g. `March - R` | `kc-pp-sync-prev-recurring` | `15,35,55 * * * *` UTC |
| `dashboard` | Dashboard-only refresh | `kc-pp-sync-dashboard` | `18,38,58 * * * *` UTC |
| `all-prev` | older month backfill lane | `kc-pp-sync-older` | `0 */4 * * *` UTC |

Confirm scheduler state when the schedule matters:

```bash
gcloud scheduler jobs list --location us-central1 --project aya-gservicies \
  --format='table(name,schedule,timeZone,httpTarget.body)'
```

## What Each Sync Updates

Exact one-off tab sync:
- reads job numbers from the source month tab
- pulls Jobber + HeyPros data
- updates only auto-owned columns on that tab
- refreshes that month's `GTP $` tab when present
- refreshes Dashboard and profitability
- writes the month margin header in `C1` when available
- refreshes relevant conditional formatting
- appends a result to `Log`

Exact recurring tab sync:
- reads recurring rows from the `- R` tab
- pulls Jobber + HeyPros data
- updates recurring auto-owned columns
- skips `GTP $` refresh
- refreshes Dashboard and profitability
- refreshes relevant conditional formatting
- appends a result to `Log`

Dashboard mode:
- refreshes Dashboard payment stats and profitability only
- appends a Dashboard result to `Log`

All-prev mode:
- discovers bare one-off month tabs older than the previous LA month, excluding January
- self-calls exact tab syncs for each older one-off tab
- self-calls matching recurring tabs if they exist
- refreshes Dashboard and profitability at the end
- appends an `all-prev` result to `Log`

## Verification

Prefer the API response first. A clean exact-tab response looks like:

```json
{
  "status": "ok",
  "elapsed": "62.6s",
  "tab": "April - R",
  "recurring": true,
  "jobNumbers": 22,
  "updatedRows": 47,
  "gtpRows": 0,
  "dashboardJobs": 615
}
```

If the response is missing, ambiguous, or failed, read Cloud Run logs:

```bash
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="kc-pp-sync"' \
  --project aya-gservicies --limit 50
```

Optional sheet-side verification:

```bash
gog sheets get 1p4lxIUjWFYNDp6ptqSMwyRcdle5Hcv5UMC6TdpZE99Q 'Log!A:H' --plain
```

Report the target, completion state, and row/job evidence. If verification is partial, say exactly which evidence confirmed the run.
