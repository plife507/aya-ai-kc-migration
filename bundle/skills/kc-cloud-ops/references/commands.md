# KC Cloud Ops Command Patterns

## Pre-Deploy

```bash
git status --short --branch
git rev-parse HEAD
gcloud auth list
gcloud config get-value project
gcloud run services describe <service> --region <region> --project <project>
gcloud run revisions list --service <service> --region <region> --project <project>
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="<service>"' --project <project> --limit 50
```

## Deploy

```bash
gcloud run deploy <service> \
  --source . \
  --region <region> \
  --project <project> \
  --no-allow-unauthenticated \
  --memory 512Mi \
  --cpu 0.1666 \
  --timeout 300 \
  --max-instances 1
```

When secrets are involved, prefer:

```bash
--update-secrets=ENV_NAME=SECRET_NAME:latest,...
```

Keep non-secret runtime config in:

```bash
--set-env-vars=KEY=value,...
```

## Post-Deploy

```bash
gcloud run services describe <service> --region <region> --project <project> --format='yaml(status.url,status.latestReadyRevisionName,status.traffic)'
gcloud run revisions list --service <service> --region <region> --project <project>
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="<service>"' --project <project> --limit 50
```

## Safe Sheets Verification

```bash
gog sheets metadata <sheetId> --json
gog sheets get <sheetId> "Tab!A1:O5" --json --no-input
```

## Failure Patterns To Check First

- CLI `main()` executed on import and killed the Functions Framework process.
- `dist/` artifact stale relative to `src/`.
- Secret exists but runtime service account cannot access it.
- Function target name does not match the exported symbol.
- A startup probe error is masking a fast process exit in revision logs.
