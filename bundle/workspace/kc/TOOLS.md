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

KC uses the shared Aya skill store. Canonical skills live at `/home/plife507/AYA-CLAW/skills`; `/home/plife507/AYA-CLAW/kc/skills` is a symlink to that canonical directory, not a separate copy.

---

Add whatever helps you do your job. This is your cheat sheet.

## KC Sales Sync / Dashboard

- Repo: `/home/plife507/Projects/KC-SALES-SYNC`
- Project/system: KC Sales Sync + KC Sales Dashboard.
- This repo contains two Cloud Run services from one codebase:
  - `kc-sales-sync`
  - `kc-sales-dashboard`
- GCP project: `aya-gservicies` (Aya's Google Cloud home for services/modules)
- Region: `us-central1`
- Active account checked 2026-04-25: `aya@kcpowerclean.com`

## KC PP Sync

- Repo: `/home/plife507/Projects/kc-pp-sync`
- Project/system: KC PP Sync.
- This is a separate repo and separate product/code project from `KC-SALES-SYNC`.
- It is similar in shape and bootstrap context to sales sync, but it has its own scripts, service, spreadsheet, source mix, and operational flow.
- GCP project verified from repo docs 2026-04-25: `aya-gservicies` (Aya's Google Cloud home for services/modules)
- Region: `us-central1`

### Shared KC Bootstrap Context

- Sales sync and PP sync are sibling KC systems that share operational patterns, but do not merge them in notes or commands:
  - the local Jobber CLI TypeScript project is reusable boilerplate for how to talk to Jobber
  - it can be used headless for direct Jobber operations, and as a base for building new Jobber-backed tools
  - each repo now has its own custom scripts and runtime flow; do not assume they call or depend on the Jobber CLI directly
  - both repo docs currently point at Google Cloud project `aya-gservicies`, Aya's Google Cloud home where different Aya service modules can be deployed
  - both deploy Cloud Run services in `us-central1`
  - Secret Manager for production credentials
  - Google Sheets as operational output/readback
  - Slack messages as an operational input/work queue for KC job updates
  - `gcloud` for infra, `gog` for Workspace/Sheets verification
- Do not discard bootstrap-like context until it has been promoted into durable notes here or repo docs.
- Treat `/home/plife507/Projects/KC-SALES-SYNC` and `/home/plife507/Projects/kc-pp-sync` as related-but-separate KC systems. Verify repo path, service name, sheet id, env, and scheduler before acting.

### Shared Aya Local Power Commands

- Canonical command names across main, KC, agents, and topics: `Aya-dim`, `Aya-bright`, and `Aya-boost`.
- Script paths: `/home/plife507/AYA-CLAW/scripts/aya-dim`, `/home/plife507/AYA-CLAW/scripts/aya-bright`, `/home/plife507/AYA-CLAW/scripts/aya-boost`.
- Global PATH symlinks: `/home/plife507/.local/bin/aya-dim`, `/home/plife507/.local/bin/aya-bright`, `/home/plife507/.local/bin/aya-boost`.
- Deprecated aliases remain: `aya-sleep` and `aya-wakeup`. Prefer dim/bright because sleep/wake collides with chat/session behavior.

### Jobber Access

- Canonical Jobber runtime is the v3 TypeScript CLI skill/repo:
  - skill: `/home/plife507/AYA-CLAW/skills/jobber-cli-v3-operator/SKILL.md`
  - repo: `/home/plife507/Projects/jobber/jobber-cli-v3`
  - env: `/home/plife507/Projects/jobber/.env`
  - headless pattern: `JOBBER_ENV_PATH=/home/plife507/Projects/jobber/.env JOBBER_OAUTH_SKIP_AUTHORIZE=1 yarn dev ... --json`
- Older `jobber` binary path `/home/plife507/.nvm/current/bin/jobber` exists but is not the canonical current lane.
- Jobber CLI is reusable boilerplate for authenticated/throttled Jobber communication. Use it headless for direct Jobber operations, and use it as the base/pattern when building new Jobber-backed tools.
- Sales sync and PP sync were built from that TypeScript base/pattern, but they have their own custom scripts. The CLI is not a required runtime dependency for those services.
- Useful commands:

```bash
jobber doctor --machine --non-interactive
jobber status
jobber search jobs "<query>"
jobber get job <id>
jobber query "<graphql>"
jobber notes --limit 100 --max-notes 50
```

- The CLI handles local auth and throttle behavior. Do not default to raw curl/direct GraphQL for manual Jobber reads/writes.
- The `KC-SALES-SYNC` service code uses Jobber API/OAuth internally at runtime; that is implementation detail, not the normal operator workflow.
- Jobber subcontractor expense writes should use the fixed wrapper:

```bash
python3 /home/plife507/AYA-CLAW/skills/jobber-cli-v3-operator/scripts/create_subcontractor_expense.py \
  <jobNumber> --vendor "Vendor" --amount 123 --date M/D/YYYY --reason "reason"
```

- This wrapper sets title `Sub`, accounting code `subcontractors`, and date-only inputs to midday UTC to preserve the intended Pacific calendar day.

### Services

- Sync backend: `kc-sales-sync`
  - Purpose: Jobber draft quotes + notes -> Google Sheet + `Log` tab.
  - Entrypoint env: `FUNCTION_TARGET=kcSalesSync`, `FUNCTION_SOURCE=dist/function.js`
  - Cloud Run auth: private; invoker is appspot service account plus `aya@kcpowerclean.com`.
  - Current ready revision seen 2026-04-25: `kc-sales-sync-00030-pvf`
  - Scheduler: `kc-sales-sync-recurring`, every 15 minutes UTC.
- Dashboard: `kc-sales-dashboard`
  - Purpose: public dashboard reading the synced Google Sheet.
  - Entrypoint env: `FUNCTION_TARGET=kcSalesDashboard`, `FUNCTION_SOURCE=dist/dashboard-function.js`
  - Cloud Run auth: public (`allUsers` invoker), accepted current posture.
  - Current ready revision seen 2026-04-25: `kc-sales-dashboard-00021-9h9`
  - Public URL seen 2026-04-25: `https://kc-sales-dashboard-jvj77nroxa-uc.a.run.app`
  - Scheduler: `kc-sales-dashboard-refresh`, `2,17,32,47 * * * *` UTC, POSTs `/api/refresh`.

### PP Sync Operations

- Repo: `/home/plife507/Projects/kc-pp-sync`
- Service: `kc-pp-sync`
- Purpose: Jobber + HeyPros -> KC PP Sync spreadsheet, plus payment, GTP, and profitability views.
- For PP costing and Slack-ready margin output, use:
  - `/home/plife507/AYA-CLAW/skills/kc-pp-job-costing/SKILL.md`
  - `/home/plife507/AYA-CLAW/skills/kc-formatting/SKILL.md`
  - `/home/plife507/AYA-CLAW/skills/kc-slack-channel-operator/SKILL.md`
- For ad hoc PP/cost updates, Slack messages are the practical source input. Parse the Slack message first, then enrich from Jobber/quote side when Nathan asks for price or job details. Keep the Slack output focused on the job, cost, revenue, and margin; do not add sheet/payment-gating caveats unless Nathan asks.
- Slack-formatted PP/cost replies should include linked client and linked Jobber job number at the top using Slack link syntax: `<url|label>`.
- When replying in Slack threads or posting Slack updates from a Telegram request, send only one visible confirmation back to the requesting chat. Do not produce a second duplicate "done" message after the Slack/thread action succeeds.
- If Nathan asks to update Jobber job expenses, use Jobber expense APIs/CLI with a `write_expenses` scoped credential. Do not silently substitute a Sheet update if Jobber expense write is blocked; surface the blocker.
- Spreadsheet: `1p4lxIUjWFYNDp6ptqSMwyRcdle5Hcv5UMC6TdpZE99Q`
- Entrypoint: `kcPPSync` from `dist/`
- Local commands:

```bash
cd /home/plife507/Projects/kc-pp-sync
npm run build
npm test
npm run local
```

- Manual Cloud Run invocation uses an identity token and mode body:

```bash
TOKEN=$(gcloud auth print-identity-token)
curl -X POST https://kc-pp-sync-823212137840.us-central1.run.app \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mode":"current"}'
```

- Mode values: `current`, `current-r`, `prev`, `prev-r`; specific tab by name can use `{"tab":"February"}`.
- Scheduler jobs seen in repo docs:
  - `kc-pp-sync-hourly`
  - `kc-pp-sync-recurring`
  - `kc-pp-sync-prev-month`
  - `kc-pp-sync-prev-recurring`
  - plus dashboard/older jobs seen live: `kc-pp-sync-dashboard`, `kc-pp-sync-older`
- Local secret source of truth: `~/.secrets/aya/kc-pp-sync.env`; repo `.env.local` may symlink there.
- HeyPros is a live source for PP sync. The project should stay read-only against HeyPros unless Nathan explicitly approves writes.
- Major layout caution: recurring tabs do not have margin column C, so recurring column indices are offset by -1. Branch by layout instead of assuming one column map.
- PP sync repo had pre-existing changes when checked 2026-04-25: `.gitignore`, `package-lock.json`, and untracked `SECRETS.md`; do not overwrite those casually.

### Repo Commands

```bash
cd /home/plife507/Projects/KC-SALES-SYNC
npm test
npm run typecheck
npm run build
npm run sync
npm run sheet:init
npm run dashboard:data
npm run local:sync
npm run local:dashboard
```

### Runtime Shape

- Default tab: `Draft Quote Sales Touch`
- Secret-backed sheet target: `KC_SALES_SYNC_SPREADSHEET_ID`
- Cloud Run must use direct Google OAuth secrets and `ALLOW_LOCAL_SHEETS_FALLBACK=false`.
- Cloud Run Jobber runtime can use `JOBBER_ACCESS_TOKEN` or the client/secret/refresh-token trio.
- Jobber refresh token rotation is persisted best-effort to Secret Manager via `JOBBER_REFRESH_TOKEN_SECRET`.
- Quote fetches are paginated and throttled; keep `QUOTE_PAGE_SIZE` small, currently `5`, and do not replace this with a single large Jobber query.

### Important Gotchas

- The same repo deploys two services. Always set the right `FUNCTION_TARGET` and `FUNCTION_SOURCE`.
- `src/index.ts` must not run CLI `main()` on import; Cloud Run imports the function module.
- Conditional formatting ownership is column L only, using helper column O. Do not reintroduce column M formatting.
- The sheet freezes header row and first 3 columns; layout is defined in `src/config/layouts.ts`.
- Dashboard reads from Sheets, not directly from Jobber. Flow is Jobber -> `kc-sales-sync` -> Sheet -> dashboard.
- `GET /data/live-data.json` and `POST /api/refresh` worked on 2026-04-25. `GET /healthz` returned a Google 404 despite being documented in code; check route/platform behavior before relying on it.

### Safe Deploy Pattern

```bash
gcloud run deploy kc-sales-sync --source . --region us-central1 --project aya-gservicies ...
gcloud run deploy kc-sales-dashboard --source . --region us-central1 --project aya-gservicies ...
```

Before deploy: `git status --short --branch`, `npm test`, `npm run typecheck`, `npm run build`, inspect live service config/revisions. After deploy: confirm ready revision, traffic, endpoint smoke, logs, and sheet readback when a sync writes.
