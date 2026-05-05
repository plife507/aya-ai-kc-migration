# Claude Development Guide — jobber workspace

**Scope**: Two CLIs for the Jobber GraphQL API + shared OAuth bridge.
**Not in scope**: Anything outside `/home/plife507/Projects/jobber/`.

## Current Focus

Porting v2.5 JS (nested in `jobber-cli-v3/reference/jobber-cli/`) → `jobber-cli-v3/` (TypeScript v3.0.0). See [`jobber-cli-v3/PHASES.md`](./jobber-cli-v3/PHASES.md).

**API writes disabled** during the port. All mutations must be gated behind `JOBBER_WRITES_ENABLED=1`.

## Layout

| Path | Purpose |
|---|---|
| `jobber-cli-v3/` | v3.0 TS CLI — active development target (own git repo) |
| `jobber-cli-v3/reference/jobber-cli/` | v2.5 JS CLI clone — reference only, not built |
| `oauth/` | Python OAuth manager (shared subprocess dependency) |
| `scripts/` | Shell helpers |
| `tokens/` | Runtime token cache (gitignored) |
| `.env` | Shared credentials (gitignored) |

Both CLIs read the same `.env` (workspace root) and `tokens/jobber_tokens.json`. Don't fork the token store.

## Ground Rules

1. **Feature parity first.** Port v2.5 behavior exactly into v3.0. Improvements after cutover.
2. **Strict TS.** `strict` + `noUncheckedIndexedAccess` + `exactOptionalPropertyTypes`. No `any`.
3. **Boundary validation.** Use Zod for `.env`, subprocess stdout, and cached JSON.
4. **Never bypass throttle.** All GraphQL queries go through the typed client's `executeQuery`.
5. **Never bypass writes-disabled gate.** Mutations require `JOBBER_WRITES_ENABLED=1`.
6. **Preserve OAuth Python.** Don't rewrite it in TS — it works, shell out to it.

## Key Patterns (Inherited from v2.5)

- **BaseCommand pattern**: all commands extend a common base that injects client/throttle/schema/error handlers and handles OAuth refresh + cleanup.
- **Event-driven throttle**: `ThrottleManager` emits status updates; client auto-waits when budget is insufficient.
- **Schema-aware error recovery**: validation errors are matched against cached schema for suggestions.
- **Atomic `.env` writes**: temp file + rename; no partial writes.

Detailed patterns live in `jobber-cli-v3/reference/jobber-cli/CLAUDE.md` (legacy reference) — apply the same logic in TS with types.

## Rate Limits

- Budget: 10,000 throttle units max
- Schema introspection: ~45,000 units (cache and reuse)
- Min request delay: 200ms, dynamic up to 2000ms
- Max retries: 3 with exponential backoff

## Running Commands

```bash
# Legacy (JS) — during migration, reference only
node jobber-cli-v3/reference/jobber-cli/bin/jobber <cmd>

# New (TS) — under development
cd jobber-cli-v3 && yarn dev <cmd>        # via tsx, no build
# or after yarn build:
node jobber-cli-v3/bin/jobber.js <cmd>

# OAuth manual refresh
python3 oauth/jobber_oauth_manager.py get-token
```

## Communication Style

Be concise. Skip filler ("Perfect!", "Excellent!"). Lead with action/result. One-line comments when needed, none when not. No intermediate `.md` progress reports.
