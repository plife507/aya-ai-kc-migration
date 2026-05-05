# AYA-AI KC Migration Bundle

This repo is the migration payload for rebuilding the KC-focused Aya / AYA-AI runtime on a new system.

It now contains the actual bundle, not just instructions.

## Important

This repo must stay private. It excludes live credentials, but it contains operational memory, client/job workflow context, channel IDs, sheet IDs, runbooks, and system notes.

Live secrets are not bundled. Rehydrate credentials on the target host from the secret source of truth, Secret Manager, or newly rotated credentials.

## Quick Start

```bash
git clone https://github.com/plife507/aya-ai-kc-migration.git
cd aya-ai-kc-migration
make validate
./scripts/install-bundle.sh --dry-run
```

When the dry run looks right:

```bash
./scripts/install-bundle.sh --target "$HOME/.openclaw" --projects "$HOME/Projects"
./scripts/apply-telegram-visibility-profile.sh --check-runtime
```

## What Is Bundled

- `bundle/workspace/kc/` - KC workspace files, docs, memory notes, and operating context.
- `bundle/skills/` - canonical AYA-CLAW skill store used by KC workflows.
- `bundle/projects/jobber/` - Jobber CLI v3 source and support docs.
- `bundle/projects/kc-pp-sync/` - PP sync service source, docs, scripts, and tests.
- `bundle/projects/KC-SALES-SYNC/` - sales sync service source and docs.
- `bundle/projects/KC-SALES-SYNC-dashboard/` - dashboard service source and docs.
- `bundle/projects/CompanyCam/` - CompanyCam helper project source and docs.
- `bundle/docs/`, `bundle/references/`, `bundle/phases/` - shared runbooks and planning docs.
- `bundle/config-templates/openclaw.redacted.json` - redacted shape of the current OpenClaw config.
- `bundle/MANIFEST.files` - file inventory for the payload.

## What Is Not Bundled

- `.env`, `.env.local`, or any live env file.
- token caches.
- OAuth callback/token files.
- Google credential JSON files.
- client secret JSON files.
- keyrings.
- `.git` directories.
- dependency folders such as `node_modules`.
- generated runtime state, queues, logs, caches, and local databases.

## Restore Shape

Default install targets:

- OpenClaw target: `$HOME/.openclaw`
- Projects target: `$HOME/Projects`

The installer copies:

- `bundle/skills/` -> `$HOME/.openclaw/skills/`
- `bundle/workspace/kc/` -> `$HOME/.openclaw/workspaces/agents/kc/`
- `bundle/projects/*` -> `$HOME/Projects/*`
- `bundle/config-templates/` -> `$HOME/.openclaw/config-templates/`

It does not overwrite secrets or create live credentials.

## Rehydrate Separately

After install, rebuild secrets on the target host:

- OpenClaw channel/provider secrets.
- Slack and Telegram credentials.
- Jobber OAuth credentials and token cache.
- Google / `gog` Workspace credentials.
- CompanyCam credentials.
- Cloud Run / Secret Manager access.
- service-specific env files for `kc-pp-sync` and `KC-SALES-SYNC`.

The bundled `.env.example` and `SECRETS.md` files document the expected variables without carrying live values.

## Validation

```bash
make validate
```

Validation checks:

- bundle roots exist.
- manifest JSON parses.
- no forbidden secret/runtime filenames were bundled.
- no obvious live token/private-key patterns are present.
- required scripts are executable.

## Main Files

- `migration-payload-manifest.json` - machine-readable description of the actual payload.
- `ingestion-manifest.json` - machine-readable ingestion guidance for indexing/embedding the bundle.
- `ingestion-plan.md` - operator guidance for ingestion/chunking.
- `references-skills-runbook.md` - notes on skills and systems.
- `scripts/install-bundle.sh` - target-host restore helper.
- `scripts/apply-telegram-visibility-profile.sh` - restores the current Telegram visibility profile on the new host.
- `scripts/validate.sh` - bundle validation.
