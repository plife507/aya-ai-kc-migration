# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

Canonical skills live in `/home/plife507/AYA-CLAW/skills`. Agent workspaces should reference or symlink to that directory instead of keeping copied skill folders.

---

Add whatever helps you do your job. This is your cheat sheet.

## Jobber

- Canonical Jobber CLI repo: `/home/plife507/Projects/jobber/jobber-cli-v3`
- Jobber workspace root: `/home/plife507/Projects/jobber`
- Shared Jobber env file: `/home/plife507/Projects/jobber/.env`
- Shared Jobber token cache: `/home/plife507/Projects/jobber/tokens/jobber_tokens.json`
- Jobber OAuth manager: `/home/plife507/Projects/jobber/oauth/jobber_oauth_manager.py`
- Deterministic subcontractor expense wrapper: `/home/plife507/AYA-CLAW/skills/jobber-cli-v3-operator/scripts/create_subcontractor_expense.py`
- Old KC Jobber CLI path is deprecated; use the v3 repo above instead.

## Google Workspace / gog

- `gog` binary path: `/home/plife507/.local/bin/gog`
- Primary gog Workspace account: `aya@kcpowerclean.com`
- Gog OAuth client credentials file: `~/.config/gogcli/client_secret_aya_workspace.json`
- Authorized gog services observed: `calendar, contacts, docs, drive, gmail, sheets`
- OpenClaw/gateway PATH includes `~/.local/bin`, so `gog` should be callable directly.

## Google Cloud / gcloud

- Primary GCP project for KC runtime work: `aya-gservicies`
- Primary region: `us-central1`
- KC PP sync Cloud Run service: `kc-pp-sync`
- KC sales sync Cloud Run service: `kc-sales-sync`
- Local KC PP sync repo: `/home/plife507/Projects/kc-pp-sync`
- Local KC sales sync repo: `/home/plife507/Projects/KC-SALES-SYNC`

## Aya Local Power

- Canonical command names: `Aya-dim`, `Aya-bright`, and `Aya-boost`.
- Script paths: `/home/plife507/AYA-CLAW/scripts/aya-dim`, `/home/plife507/AYA-CLAW/scripts/aya-bright`, `/home/plife507/AYA-CLAW/scripts/aya-boost`.
- Global PATH symlinks: `/home/plife507/.local/bin/aya-dim`, `/home/plife507/.local/bin/aya-bright`, `/home/plife507/.local/bin/aya-boost`.
- `aya-dim` turns displays off, turns the Razer keyboard light off, arms key-wake, and sets `power-saver`.
- `aya-bright` restores displays, keyboard lighting, clears key-wake, and sets `balanced`.
- Deprecated aliases remain: `aya-sleep` and `aya-wakeup`. Prefer dim/bright because sleep/wake collides with chat/session behavior.

## Lane split reminder

- Use `jobber-cli-v3` for Jobber API reads/writes.
- Use `gog` for Google Workspace user data like Sheets/Gmail/Drive.
- Use `gcloud` for GCP admin/runtime work like Cloud Run, Scheduler, Secret Manager, IAM, and logs.
