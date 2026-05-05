---
name: gog-workspace-operator
description: Operate Google Workspace tools through the local `gog` CLI for Gmail, Drive, Docs, Sheets, Contacts, and Calendar. Use when Aya needs to inspect or update Google Workspace data, verify `gog` auth, decide between `gog` and `gcloud`, or troubleshoot Workspace OAuth/setup on this machine.
---

# Gog Workspace Operator

Use this skill when Google Workspace work should happen through `gog`.

## Core rule

Choose the right lane before acting:

- use `gog` for Workspace user data like Gmail, Drive, Docs, Sheets, Contacts, and Calendar
- use `gcloud` for GCP admin, Cloud Run, Scheduler, Secret Manager, IAM, and deploy work
- do not blur the two lanes just because both are Google

## Workflow

### 1. Confirm the lane

Use `gog` when the task is about:

- reading or editing Sheets
- searching Gmail
- finding or exporting Drive files
- reading Docs metadata or content
- listing calendars or events
- checking whether Workspace OAuth is healthy

If the task is really about Cloud Run, GCP auth, or service accounts, switch to `gcloud` instead.

### 2. Check auth first when anything is uncertain

Start with:

```bash
gog --version
gog auth list
```

If `gog` is missing from PATH, check the local install path before assuming setup is broken.

If auth is missing or stale, read `references/auth-and-command-map.md`.

### 3. Prefer read-first patterns

For Google Workspace work:

- inspect metadata before editing
- read the smallest range or object needed
- avoid broad writes when a narrow update will do
- separate observed facts from assumptions

### 4. For writes, be precise

Before editing Workspace data:

- confirm the target account, file, spreadsheet, tab, or range
- confirm whether this is a one-off manual fix or should be solved in code
- keep changes minimal and reversible when possible
- do not expose OAuth secrets, refresh tokens, or copied auth URLs in chat

## Common command patterns

### Sheets

```bash
gog sheets metadata <spreadsheet-id> --json
gog sheets get <spreadsheet-id> '<tab>!A1:Z20' --plain
gog sheets notes <spreadsheet-id> '<tab>!A1:Z20'
gog sheets links <spreadsheet-id> '<tab>!A1:Z20'
```

### Drive

```bash
gog drive search "query" --max 10
gog drive get <file-id> --json
```

### Gmail

```bash
gog gmail search "from:someone@example.com newer_than:7d" --max 10
```

### Calendar

```bash
gog calendar list
```

## Local reference

Read `references/auth-and-command-map.md` for:

- current local `gog` auth state
- binary and credential paths
- current account and authorized services
- common verification and recovery commands
- the Workspace vs GCP split used on this machine

## Output style

Keep replies practical:

- say what you inspected
- separate fact from interpretation
- call out auth blockers plainly
- when writing, state exactly what will change
