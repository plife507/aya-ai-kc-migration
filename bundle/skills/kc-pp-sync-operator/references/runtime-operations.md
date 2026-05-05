# KC PP Sync — Runtime Operations

## Runtime identity

GCP project:
- `aya-gservicies`

Region:
- `us-central1`

Cloud Run service:
- `kc-pp-sync`

Local repo:
- `/home/plife507/Projects/kc-pp-sync`

## Runtime role

The service:
- pulls Jobber and HeyPros data
- matches HeyPros work orders to Jobber jobs by `purchaseOrder`
- writes rows to the appropriate month or recurring tab
- refreshes GTP outputs and Dashboard
- logs every sync result to the Command tab
- refreshes Jobber OAuth tokens automatically via Secret Manager

## Mode routing

`src/config/env.ts` resolves modes this way:
- `current` -> current month one-off tab
- `current-r` -> current month recurring tab
- `prev` -> previous month one-off tab
- `prev-r` -> previous month recurring tab
- `dashboard` -> dashboard refresh path
- `all-prev` -> special previous-period path

## Scheduler pattern

Observed scheduler jobs include:
- `kc-pp-sync-hourly`
- `kc-pp-sync-recurring`
- `kc-pp-sync-prev-month`
- `kc-pp-sync-prev-recurring`
- `kc-pp-sync-dashboard`
- `kc-pp-sync-older`

Use `gcloud scheduler jobs list` and job details to confirm current schedules instead of trusting old notes.

## Manual sync lanes

For exact manual sync payloads, current source-tab map, scheduler mode map, and verification commands, read `/home/plife507/AYA-CLAW/skills/kc-pp-sync/references/manual-sync.md`.

### In-sheet lane
Use the Apps Script menu:
- open the KC PP Sync spreadsheet
- use the `KC Sync` menu
- choose the target sync

### Direct API lane
Use an authenticated Cloud Run POST.

Example:
```bash
TOKEN=$(gcloud auth print-identity-token)
curl -X POST https://kc-pp-sync-823212137840.us-central1.run.app \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mode":"current"}'
```

For a specific tab:
```bash
-d '{"tab":"February"}'
```

Prefer narrow mode or tab targeting when investigating.

Do not use `gcloud run jobs execute`; this service is invoked by HTTP POST, and Scheduler jobs use the same body modes documented in the manual sync runbook.

## Core inspection commands

### Cloud Run service

```bash
gcloud run services describe kc-pp-sync --region us-central1 --project aya-gservicies
```

### Scheduler inventory

```bash
gcloud scheduler jobs list --location us-central1 --project aya-gservicies
```

### Recent logs

```bash
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="kc-pp-sync"' --project aya-gservicies --limit 20
```

### Deploy

```bash
gcloud run deploy kc-pp-sync \
  --source . \
  --region us-central1 \
  --project aya-gservicies \
  --no-allow-unauthenticated
```

## Recommended runtime-check order

When diagnosing runtime issues:
1. inspect Cloud Run service details
2. inspect latest revision state
3. inspect scheduler jobs and cadence
4. inspect recent logs
5. inspect repo docs/code if behavior still needs explanation

Keep runtime diagnosis in its own lane.
If the broader KC request also involves Slack posting, Jobber writes, or costing decisions, inspect the runtime first, then hand off the downstream work to the proper lane instead of mixing them during diagnosis.

## Access model

Working auth lanes:
- `gog` user OAuth for Workspace reads and sheet work
- `gcloud` user auth for GCP admin and inspection
- Cloud Run service account for production runtime

## Runtime cautions

- Treat service-account choice and IAM findings carefully; hardening issues are not always the immediate cause of a sync symptom.
- Do not expose Secret Manager values in chat.
- Prefer read-only inspection first when production is healthy and the issue is not yet localized.
