# Gog auth and command map

## Purpose

This note captures the current local `gog` setup and the command patterns Aya should prefer.

## Current local truth

- binary path: `/home/plife507/.local/bin/gog`
- observed version during setup: `v0.12.0`
- authenticated account: `aya@kcpowerclean.com`
- authorized services: `calendar, contacts, docs, drive, gmail, sheets`
- auth storage type observed: OAuth user auth
- gateway PATH includes `~/.local/bin`, so OpenClaw can use `gog`

## Lane split

Use:

- `gog` for Workspace user data
- `gcloud` for GCP admin and deploy work
- Cloud Run or service accounts for app runtime auth

Do not use local runtime credentials for apps that only run in Cloud Run unless there is a real local-runtime need.

## Verify auth

```bash
gog --version
gog auth list
```

Useful signs:

- account is listed
- expected services are present
- there is no prompt suggesting missing credentials

## Auth setup and recovery

Credential file used during setup:

```bash
~/.config/gogcli/client_secret_aya_workspace.json
```

Commands used during working setup:

```bash
gog auth credentials set ~/.config/gogcli/client_secret_aya_workspace.json
gog auth add aya@kcpowerclean.com --services gmail,calendar,drive,contacts,docs,sheets --remote --step=1
gog auth add aya@kcpowerclean.com --services gmail,calendar,drive,contacts,docs,sheets --remote --step=2 --auth-url '<browser redirect url>'
```

Never echo client secrets, refresh tokens, or full redirect callback contents into normal chat replies.

## Common verification commands

```bash
gog drive search "KC" --max 3
gog sheets metadata 1p4lxIUjWFYNDp6ptqSMwyRcdle5Hcv5UMC6TdpZE99Q --json
gog calendar list
gog gmail search "newer_than:7d" --max 5
```

## Sheets patterns

Read metadata first:

```bash
gog sheets metadata <spreadsheet-id> --json
```

Read a small range:

```bash
gog sheets get <spreadsheet-id> '<tab>!A1:Z20' --plain
```

Inspect notes or links when needed:

```bash
gog sheets notes <spreadsheet-id> '<tab>!A1:Z20'
gog sheets links <spreadsheet-id> '<tab>!A1:Z20'
```

## Troubleshooting hints

If `gog` is enabled in OpenClaw config but not usable, check in this order:

1. `gog --version`
2. `gog auth list`
3. whether `~/.local/bin` is on PATH for the current execution lane
4. whether the OAuth client credential file exists
5. whether the requested Workspace service was authorized

## Cautions

- Keep Workspace auth and GCP auth mentally separate.
- Do not assume `gcloud auth` implies `gog` is ready.
- Do not paste secrets into repo files or general reports.
