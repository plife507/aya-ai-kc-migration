# Tomorrow CompanyCam Use

Use this as the simple v1 workflow for a Jobber job.

## Inputs Needed

- Job number
- Customer name or job title
- Service address
- Correct CompanyCam user to assign
- Correct checklist template

## Safe Lookup

First find the project album by address/job details. Prefer the actual project album over a jobwalk album, even when the jobwalk has more photos.

```bash
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects match --street-address-1 "<street>" --city "<city>" --state "<state>" --postal-code "<zip>" --json
```

Then inspect the selected project:

```bash
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects get <project-id> --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects assigned-users <project-id> --json
```

## Checklist Selection

List templates before applying one:

```bash
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- templates checklists list --json
```

Dry-run the checklist application:

```bash
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects apply-checklist <project-id> --checklist-template-id <template-id> --dry-run --json
```

## User Assignment

Dry-run the user assignment:

```bash
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects assign-user <project-id> --user-id <user-id> --dry-run --json
```

## Live Writes

Only run live writes after Nathan approves the exact project id, user id, and checklist template id. Enable writes for that one command only.

```bash
COMPANYCAM_WRITES_ENABLED=1 COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects assign-user <project-id> --user-id <user-id> --json

COMPANYCAM_WRITES_ENABLED=1 COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects apply-checklist <project-id> --checklist-template-id <template-id> --json
```

## Stop Conditions

- Multiple address matches: stop and surface options.
- Jobwalk and project album both exist: use the project album unless Nathan says otherwise.
- Template name is ambiguous: use the numeric template id.
- User identity is uncertain: list/export users and confirm before writing.
