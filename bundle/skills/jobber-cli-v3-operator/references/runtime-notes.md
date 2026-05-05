# Jobber CLI v3 runtime notes

## Active repo

- CLI repo: `/home/plife507/Projects/jobber/jobber-cli-v3`
- Workspace root: `/home/plife507/Projects/jobber`
- Shared env: `/home/plife507/Projects/jobber/.env`
- Token cache: `/home/plife507/Projects/jobber/tokens/jobber_tokens.json`
- OAuth manager: `/home/plife507/Projects/jobber/oauth/jobber_oauth_manager.py`
- Local Python venv for OAuth: `/home/plife507/Projects/jobber/.venv`

## Shipped status

`TODO.md` says v3.0.0 shipped on 2026-04-17 and no phase is currently active.
All phases 0-6 are complete.

## Canonical headless invocation

```bash
cd /home/plife507/Projects/jobber/jobber-cli-v3
JOBBER_ENV_PATH=/home/plife507/Projects/jobber/.env \
JOBBER_OAUTH_SKIP_AUTHORIZE=1 \
yarn dev <command> [args...] --json
```

For writes:

```bash
cd /home/plife507/Projects/jobber/jobber-cli-v3
JOBBER_WRITES_ENABLED=1 \
JOBBER_ENV_PATH=/home/plife507/Projects/jobber/.env \
JOBBER_OAUTH_SKIP_AUTHORIZE=1 \
yarn dev job-note create 12241 --message "hi" --json
```

## Important operating rules

- Always pass `JOBBER_ENV_PATH` explicitly.
- Always pass `JOBBER_OAUTH_SKIP_AUTHORIZE=1` in agent/headless flows.
- Always prefer `--json`.
- Never export `JOBBER_WRITES_ENABLED` globally.
- Prefer `token check --json` as a liveness probe.
- Run `doctor --json` at batch start.
- Treat exit code 3 as auth handling, not blind retry.
- Treat exit code 4 as backoff, not tight retry.
- Treat exit code 10 writes-disabled as a deliberate safety gate.

## Current active command surface

- `status`
- `token check`
- `token oauth-refresh`
- `token oauth-authorize`
- `get`
- `query`
- `search`
- `notes`
- `schema fetch|analyze|help`
- `doctor`
- `job-note list|create|edit|delete`
- `job-expense list|create|edit|delete`

## Deprecated direction

Old guidance pointing at `/home/plife507/Projects/KC/jobber-cli` is deprecated.
Do not use that path for current Jobber operations or new instructions.
