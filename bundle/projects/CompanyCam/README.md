# CompanyCam

Operational integration workspace for KC CompanyCam workflows.

## Purpose

This repo is the starting point for CompanyCam automation and tooling. Keep the first version narrow: understand the API, define the workflows KC actually needs, then build the smallest reliable tool around those workflows.

## Initial Goals

- Document the CompanyCam API/auth model.
- Identify the core KC workflows:
  - project lookup
  - photo retrieval
  - job/project matching
  - upload or sync behavior, if needed
- Keep production writes gated until the exact action is approved.
- Build repeatable scripts or a small service once the workflow is clear.

## Repo Layout

- `docs/project-brief.md` - working product brief and decisions.
- `docs/api-notes.md` - CompanyCam API notes and open questions.
- `docs/setup.md` - token setup and first connection steps.
- `docs/tomorrow-use.md` - short operator flow for the first live project/user/checklist run.
- `scripts/` - original read-only Python helpers.
- `src/` - TypeScript CompanyCam CLI source.
- `bin/companycam.js` - built CLI entrypoint.

## Safety

Do not commit API tokens, customer private data, downloaded photos, or production exports. Use environment variables or a local ignored `.env` file for secrets.

## CompanyCam CLI

Install local tooling once:

```bash
npm install
```

Run CLI commands through the repo-local dev entrypoint:

```bash
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- status --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- doctor --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- token check --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- users export --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- templates checklists list --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects list --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects create --name "TEST - KC API Write Test" --dry-run --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects match --address "123 Main St, City, ST" --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects sync-job --job-number 20482 --title "Espinoza Cable Construction - Blast and Seal" --street-address-1 "123 Main St" --city "City" --state ST --checklist-template-id 61791 --dry-run --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects get <id> --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects photos <id> --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects assigned-users <id> --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects assign-user <id> --user-id <user-id> --dry-run --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects apply-checklist <id> --checklist-template-id 61791 --dry-run --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects merge --source-project-id <duplicate-id> --target-project-id <keeper-id> --archive-empty-source --dry-run --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- checklists list --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- pp template --json
```

Build and run the compiled CLI:

```bash
npm run build
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env node bin/companycam.js status --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env node bin/companycam.js doctor --json
```

Headless contract:

- Use `COMPANYCAM_ENV_PATH` explicitly; do not rely on the caller's working directory.
- Prefer `--json` for automation.
- `doctor`, `status`, `--help`, `--version`, and `projects create --dry-run` do not call CompanyCam.
- Networked commands use `COMPANYCAM_TIMEOUT_MS` with a default of 30000 ms.
- `COMPANYCAM_BASE_URL` can point tests at a local mock server when needed.
- Live project creation, title update, user assignment, or checklist creation is refused unless that single command is run with `COMPANYCAM_WRITES_ENABLED=1`.

Exit codes:

- `0` success
- `2` validation error
- `3` auth failure
- `4` rate limit
- `5` not found
- `6` config error
- `10` write-disabled refusal or internal error

The CLI is read-only by default against CompanyCam. Live project creation, title update, user assignment, checklist creation, or empty-source duplicate archive is available only when the individual command is run with `COMPANYCAM_WRITES_ENABLED=1`; use `--dry-run` first to preview the exact request. `projects sync-job` searches by address first, updates the existing project title if the Jobber number is missing, creates a project only when no address match exists, and can plan/apply one checklist template by id or name. `projects assign-user` and `projects apply-checklist` handle the simpler tomorrow workflow once the correct project album is selected. `projects merge --archive-empty-source` handles only verified empty duplicates because CompanyCam's public Core API does not expose full web-app project merge; non-empty duplicates must be merged in the CompanyCam web app so photos/files/reports/pages transfer correctly. The CLI can also write local ignored export/template files under `exports/`.

## Read-Only Connection Check

1. Copy `.env.example` to `.env`.
2. Put the CompanyCam access token in `.env` as `COMPANYCAM_API_TOKEN=...`.
3. Run:

```bash
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- token check --json
```

The check only calls read endpoints: `/company` and `/users/current`. The older Python smoke check remains available at `scripts/companycam_check.py`.
