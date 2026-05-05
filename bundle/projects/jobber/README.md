# jobber

Workspace for the Jobber API integration. Houses the new TypeScript CLI plus shared infrastructure; a clone of the legacy JS CLI lives inside the new app's `reference/` directory.

## Layout

```
jobber/
├── jobber-cli-v3/            v3.0.0 TS — the new application (own git repo)
│   └── reference/jobber-cli/ v2.5.0 JS clone (reference only)
├── oauth/                    Python OAuth manager (shared)
├── scripts/                  Shell helpers
├── tokens/                   Runtime token cache (gitignored)
├── .env                      Shared credentials (gitignored)
└── .env.example
```

`jobber-cli-v3/` has its own git history and may be pushed as a standalone repo. The workspace root is also a git repo holding `oauth/`, `scripts/`, and shared config.

## Current Focus

Migrating v2.5 JS (nested in `jobber-cli-v3/reference/jobber-cli/`) → `jobber-cli-v3/` (TS). See [`jobber-cli-v3/PHASES.md`](./jobber-cli-v3/PHASES.md) for roadmap.

**API writes are currently disabled on the Jobber side** during the port. Mutation commands are gated behind `JOBBER_WRITES_ENABLED=1`.

## Setup

```bash
cp .env.example .env              # fill in OAuth credentials + access token
python3 -m venv oauth/.venv && source oauth/.venv/bin/activate
pip install -r oauth/requirements.txt

# Legacy CLI (reference only, inside v3 repo)
cd jobber-cli-v3/reference/jobber-cli && yarn install

# New TS CLI
cd jobber-cli-v3 && yarn install && yarn build
```

## Global Install Note

The `jobber` command in PATH still points to the original KC location (`/home/plife507/Projects/KC/jobber-cli/bin/jobber`). Until Phase 6 cutover, use:

- Legacy: `jobber <cmd>` (global) or `node jobber-cli-v3/reference/jobber-cli/bin/jobber <cmd>`
- New: `cd jobber-cli-v3 && yarn dev <cmd>` or `node jobber-cli-v3/bin/jobber.js <cmd>` after `yarn build`

## OAuth

Tokens expire hourly. OAuth manager auto-refreshes when invoked via CLI subprocess. Manual refresh:

```bash
python3 oauth/jobber_oauth_manager.py get-token
```
