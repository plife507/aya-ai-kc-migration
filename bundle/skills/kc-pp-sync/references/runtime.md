# KC PP Sync Runtime Reference

## Runtime identity

GCP project:
- `aya-gservicies`

Region:
- `us-central1`

Cloud Run service:
- `kc-pp-sync`

Service URL:
- `https://kc-pp-sync-823212137840.us-central1.run.app`

Local repo:
- `/home/plife507/Projects/kc-pp-sync`

## Direct API lane

For the full manual sync runbook, exact tab map, scheduler mode map, and verification posture, read `manual-sync.md`.

Get an identity token:

```bash
TOKEN=$(gcloud auth print-identity-token)
```

Trigger an exact tab sync:

```bash
curl -X POST https://kc-pp-sync-823212137840.us-central1.run.app \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tab":"March"}'
```

Trigger a recurring tab sync:

```bash
curl -X POST https://kc-pp-sync-823212137840.us-central1.run.app \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tab":"March - R"}'
```

Replace the tab value with the exact requested month tab, for example:
- `{"tab":"February"}`
- `{"tab":"April"}`
- `{"tab":"May - R"}`

Trigger dashboard refresh:

```bash
curl -X POST https://kc-pp-sync-823212137840.us-central1.run.app \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mode":"dashboard"}'
```

## Verification lane

If the API response is incomplete, verify in Cloud Run logs:

```bash
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="kc-pp-sync"' \
  --project aya-gservicies --limit 50
```

Look for:
- target tab name
- completion lines
- row/update counts
- errors/failures

## Practical posture

- Prefer exact `tab` targeting over broad mode runs when the user names a tab.
- Do not escalate into broad troubleshooting unless the sync fails or verification is unclear.
- If the POST returns unclearly but logs show the sync completed, report the sync as completed and mention the verification source.
- Keep this as a narrow runtime lane. If the broader KC request also involves sheet diagnosis, Jobber truth, costing, or Slack delivery, route those as separate steps rather than letting the sync call absorb the whole workflow.
