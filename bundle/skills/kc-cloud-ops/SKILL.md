---
name: kc-cloud-ops
description: "Use this skill for KC Google Cloud and Google Workspace operational work: Cloud Run deploys, revision/log inspection, Secret Manager wiring, scheduler checks, and Google Sheets verification with `gog`. Trigger it when working on KC services such as `kc-pp-sync` or `kc-sales-sync`, especially when the task involves deploy/debug/verify loops or config drift."
---

# KC Cloud Ops

## Overview

Use `gcloud` as the primary tool for Cloud Run, Secret Manager, Scheduler, IAM, builds, revisions, and logs. Use `gog` only for Google Workspace-side checks, mainly Sheets verification after a sync.

## Tool Split

- `gcloud`: Cloud Run services, revisions, source deploys, logs, Scheduler, IAM, Secret Manager, Artifact Registry.
- `gog`: Sheets metadata, range reads, and safe readback verification after a sync.
- Local file reads: deployment docs, repo scripts, `.env.example`, handoff notes, and comparable repos such as `kc-pp-sync`.

## Standard Workflow

1. Inspect before changing.
   - Check `git status`, current branch, and deployable commit.
   - Confirm `gcloud auth list` and `gcloud config get-value project`.
   - Inspect the live service with `gcloud run services describe ...`.
   - Inspect revisions with `gcloud run revisions list ...`.
   - Read recent logs with `gcloud logging read ...`.
2. Compare against the known-good KC pattern.
   - If a comparable repo exists, read its `package.json`, `tsconfig.json`, deploy docs, and any migration handoff notes first.
   - Prefer the existing KC source deploy path over inventing Docker or ad hoc runtime shapes.
3. Deploy carefully.
   - Prefer `gcloud run deploy <service> --source .`.
   - Capture the exact command, resulting revision, and service URL.
   - Use Secret Manager bindings for secrets instead of plain env values when practical.
4. Verify end to end.
   - Confirm the new revision exists and receives traffic.
   - Hit the service endpoint with a safe request.
   - Check logs for startup, auth, or runtime failures.
   - If the service writes to Sheets, verify the write with `gog sheets get ...`.
5. Report operationally.
   - Deployed commit, previous revision, new revision, traffic state, verification result, warnings, rollback command.

## KC Cloud Run Defaults

- Prefer `us-central1` unless the repo or deploy docs explicitly say otherwise.
- Keep timezone env explicit when sheet-facing dates matter:
  - `TZ=America/Los_Angeles`
- Follow the Functions Framework source-deploy pattern used by `kc-pp-sync` when applicable.

## Secret Handling

- Shared secrets are acceptable only when that is the current agreed runtime contract.
- Service-specific targets such as `SPREADSHEET_ID` should usually get service-specific secret names.
- Before relying on secrets at runtime, verify:
  - the secret exists
  - the intended version is enabled
  - the Cloud Run service account has `roles/secretmanager.secretAccessor`

## Log Reading Rules

- Read the revision-specific logs, not just the generic service error.
- When startup fails, check for:
  - wrong `start` command
  - module import side effects
  - missing env/secret at import time
  - Functions Framework target/source mismatch
  - package/build artifact mismatch

## `gog` Usage

Use `gog` for Workspace-side verification, not for Cloud Run infra.

Common checks:
- `gog sheets metadata <sheetId> --json`
- `gog sheets get <sheetId> "Tab!A1:O5" --json --no-input`

Avoid using `gog` as the primary deploy tool. `gcloud` owns deploy, logs, revisions, secrets, and scheduler work.

## References

- For reusable command patterns, read [references/commands.md](references/commands.md).
- For a repo-specific handoff state, read the repo note first if one exists.
