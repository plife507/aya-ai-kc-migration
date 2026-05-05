# AYA-AI KC References, Skills, Tips, And Tricks

## Purpose

This file captures the practical references needed to migrate KC Power Clean workflows into AYA-AI without losing the rules, shortcuts, and safety practices that already work.

Use this as the operator runbook during the migration.

## Repository And Workspace References

### Main KC Workspace

- Local path: `/home/plife507/AYA-CLAW/kc`
- Project folder: `/home/plife507/AYA-CLAW/kc/projects/aya-ai-kc-migration`
- Main migration plan: `/home/plife507/AYA-CLAW/kc/projects/aya-ai-kc-migration/README.md`
- KC docs:
  - `/home/plife507/AYA-CLAW/kc/docs/pp-job-workflow.md`
  - `/home/plife507/AYA-CLAW/kc/docs/pp-recurring-jobs.md`
- Reports folder:
  - `/home/plife507/AYA-CLAW/kc/reports`

Note: this KC workspace does not currently show a configured Git remote. Treat it as a local operational workspace unless a remote is added later.

### Canonical Skills Store

- Local path: `/home/plife507/AYA-CLAW/skills`
- KC workspace link: `/home/plife507/AYA-CLAW/kc/skills -> ../skills`

Important rule: do not copy skills into the KC folder. Update the canonical skill once in `/home/plife507/AYA-CLAW/skills` so all agents inherit the same behavior.

### Jobber CLI v3

- Local repo: `/home/plife507/Projects/jobber/jobber-cli-v3`
- GitHub remote: `https://github.com/plife507/jobber-cli-v3.git`
- Shared env: `/home/plife507/Projects/jobber/.env`
- Token cache: `/home/plife507/Projects/jobber/tokens/jobber_tokens.json`
- OAuth manager: `/home/plife507/Projects/jobber/oauth/jobber_oauth_manager.py`

Canonical headless invocation:

```bash
cd /home/plife507/Projects/jobber/jobber-cli-v3
JOBBER_ENV_PATH=/home/plife507/Projects/jobber/.env \
JOBBER_OAUTH_SKIP_AUTHORIZE=1 \
yarn dev <command> [args...] --json
```

For writes, add the write gate only to that one command:

```bash
JOBBER_WRITES_ENABLED=1 \
JOBBER_ENV_PATH=/home/plife507/Projects/jobber/.env \
JOBBER_OAUTH_SKIP_AUTHORIZE=1 \
yarn dev job-expense create ... --json
```

Never export `JOBBER_WRITES_ENABLED` globally.

## Skills To Migrate Into AYA-AI

### Phase 1: Required

#### `kc-pp-job-costing`

Source:

- `/home/plife507/AYA-CLAW/skills/kc-pp-job-costing/SKILL.md`

Purpose:

- PP job costing
- Margin calculation
- Slack-ready PP posts
- `PPFLOW` command workflow
- Jobber expense plus CompanyCam setup flow

Key references:

- `/home/plife507/AYA-CLAW/skills/kc-pp-job-costing/references/costing-rules.md`
- `/home/plife507/AYA-CLAW/skills/kc-pp-job-costing/references/pp-human-in-loop-workflow.md`
- `/home/plife507/AYA-CLAW/skills/kc-pp-job-costing/references/pp-companycam-assignments.json`

Key script:

- `/home/plife507/AYA-CLAW/skills/kc-pp-job-costing/scripts/pp_job_workflow.py`

Migration note:

- This is the highest-value first workflow. Move it first after Telegram, Slack, Jobber, and CompanyCam connections work.

#### `jobber-cli-v3-operator`

Source:

- `/home/plife507/AYA-CLAW/skills/jobber-cli-v3-operator/SKILL.md`

Purpose:

- Canonical Jobber API read/write work
- Job lookup
- Notes
- Expenses
- Unassigned visit audits
- OAuth-aware CLI usage

Key scripts:

- `/home/plife507/AYA-CLAW/skills/jobber-cli-v3-operator/scripts/create_subcontractor_expense.py`
- `/home/plife507/AYA-CLAW/skills/jobber-cli-v3-operator/scripts/find_unassigned_visits.py`

Migration note:

- Do not use deprecated older Jobber CLI paths. AYA-AI should use Jobber CLI v3 as the only default Jobber runtime.

#### `kc-slack-channel-operator`

Source:

- `/home/plife507/AYA-CLAW/skills/kc-slack-channel-operator/SKILL.md`

Purpose:

- Top-level Slack posts
- Thread replies
- Cross-surface Telegram-to-Slack operations
- Delivery truth: sent vs forwarded vs unconfirmed

Important channels:

- `#pp-dispatch-mgmt` / `C08CTUF1T7C`
- `#ops-frontstage` / `C07QEEN75EU`
- `#dispatch-pm` / `C07U7Q01Q49`

Migration note:

- Slack posting must use the real Slack message lane and confirm delivery/read-back for important posts.

#### `kc-slack-thread-resolver`

Source:

- `/home/plife507/AYA-CLAW/skills/kc-slack-thread-resolver/SKILL.md`

Purpose:

- Bind exact Slack threads before replying.

Migration note:

- Use this when a request says "reply in that thread" or refers to a Slack conversation indirectly.

#### `kc-pp-sync`

Source:

- `/home/plife507/AYA-CLAW/skills/kc-pp-sync/SKILL.md`

Purpose:

- Trigger exact KC PP sheet syncs.
- Sync exact month tabs, recurring tabs, or dashboard mode.

Key references:

- `/home/plife507/AYA-CLAW/skills/kc-pp-sync/references/manual-sync.md`
- `/home/plife507/AYA-CLAW/skills/kc-pp-sync/references/runtime.md`

Migration note:

- This is a narrow action skill. Use it when the target sync is already clear.

#### `kc-pp-sync-operator`

Source:

- `/home/plife507/AYA-CLAW/skills/kc-pp-sync-operator/SKILL.md`

Purpose:

- Operate and inspect the KC PP Sync sheet and Cloud Run sync system.
- Diagnose sheet vs runtime vs business-rule problems.

Key references:

- `/home/plife507/AYA-CLAW/skills/kc-pp-sync-operator/references/sheet-architecture.md`
- `/home/plife507/AYA-CLAW/skills/kc-pp-sync-operator/references/runtime-operations.md`
- `/home/plife507/AYA-CLAW/skills/kc-pp-sync-operator/references/business-cautions.md`

Migration note:

- Use read-only inspection by default. Do not edit sheets unless explicitly approved.

#### `kc-cloud-ops`

Source:

- `/home/plife507/AYA-CLAW/skills/kc-cloud-ops/SKILL.md`

Purpose:

- Cloud Run deploys
- Logs
- Scheduler checks
- Secret Manager wiring
- Google Sheets verification with `gog`

Migration note:

- Use `gcloud` for infrastructure and `gog` for Google Workspace verification.

#### `jobber-job-identity`

Source:

- `/home/plife507/AYA-CLAW/skills/jobber-job-identity/SKILL.md`

Purpose:

- Resolve exact Jobber jobs before acting.

Migration note:

- Never guess a Jobber id from visible job number. Search and match the exact `jobNumber`.

#### `jobber-job-url-lookup`

Source:

- `/home/plife507/AYA-CLAW/skills/jobber-job-url-lookup/SKILL.md`

Purpose:

- Produce verified Jobber URLs for Slack links.

Migration note:

- Build Slack job links from verified Jobber URLs, not guessed URL patterns.

### Phase 1: Useful Support Skills

#### `openclaw-config-operator`

Source:

- `/home/plife507/AYA-CLAW/skills/openclaw-config-operator/SKILL.md`

Purpose:

- OpenClaw configuration and migration setup.

#### `openclaw-browser-operator`

Source:

- `/home/plife507/AYA-CLAW/skills/openclaw-browser-operator/SKILL.md`

Purpose:

- Browser workflow setup or verification where CLI/API access is not enough.

#### `gog-workspace-operator`

Source:

- `/home/plife507/AYA-CLAW/skills/gog-workspace-operator/SKILL.md`

Purpose:

- Google Workspace operations, especially Sheets verification.

#### `kc-formatting`

Source:

- `/home/plife507/AYA-CLAW/skills/kc-formatting/SKILL.md`

Purpose:

- KC-facing formatting rules and executive summaries.

### Phase 2: Later Skills / Workflows

#### Sales

Likely sources:

- Jobber quote / client lookup through `jobber-cli-v3-operator`
- Future `kc-sales-sync` or sales-specific skill if created

Planned use:

- Leads
- Estimates
- Follow-ups
- Pipeline summaries

#### Marketing

Likely sources:

- CompanyCam media review
- Slack review data
- Website/social workflows if approved later

Planned use:

- Reviews
- Photos
- Campaigns
- Before-and-after content

#### Reporting / Dashboards

Likely sources:

- KC PP Sync sheet
- Google Sheets
- GCloud logs
- Slack activity
- Jobber reports

Planned use:

- Daily/weekly summaries
- KPI dashboards
- Finance margin reports
- Ops reports

## Tricks And Tips

### General Migration Tips

- Start with one OpenClaw system and internal modules. Do not split into separate systems until volume or security proves it is needed.
- Keep the department split logical, not physical at first: HQ, PP, Ops, Finance, then Sales/Marketing/Reporting later.
- Route task packets, not full conversation history.
- Keep Nathan personal memory out of AYA-AI.
- Treat Jobber, CompanyCam, Slack, and Sheets as systems of record; do not let memory become the source of truth.

### PP Workflow Tips

- Use `PPFLOW` for lean PP job execution.
- Do a dry run first, then apply only after the match is clean.
- Use Jobber job number to resolve the exact job.
- Use quote-side sale and discounts for margin.
- Use Jobber expense line/vendor as the subcontractor source of truth when available.
- Use reviewed CompanyCam mappings, not loose name matching.
- Prefer existing CompanyCam project from Jobber custom field.
- Create a CompanyCam project only with explicit approval or clear flag.
- For recurring jobs, pass the known CompanyCam project id and use a fresh checklist when needed.
- Always verify Slack delivery after posting.

### Jobber Tips

- Use Jobber CLI v3 only.
- Always set `JOBBER_ENV_PATH` explicitly.
- Always set `JOBBER_OAUTH_SKIP_AUTHORIZE=1` for headless agent mode.
- Always use `--json`.
- Gate writes with `JOBBER_WRITES_ENABLED=1` only on the one write command.
- Search first and match exact `jobNumber`.
- Journal created expense/note ids before doing the next mutation.
- Do not run parallel mutations against the same Jobber account.

### CompanyCam Tips

- Reuse existing albums whenever possible.
- Prefer CompanyCam project id from Jobber custom field.
- Stop and ask when project match is ambiguous.
- Do not infer user assignments from subcontractor names.
- Use reviewed CompanyCam user ids from `pp-companycam-assignments.json`.
- Read back assigned users and checklists after every write.
- Empty duplicate projects can be archived/merged carefully; non-empty duplicates require web merge.

### Slack Tips

- For top-level channel posts, use the real Slack message lane.
- Do not treat an inter-session handoff as proof of Slack delivery.
- Verify read-back before saying a message was posted.
- Keep Telegram completion notes short.
- Use exact Slack thread binding before replying in a thread.
- For PP costing posts, only use `#pp-dispatch-mgmt` unless Nathan explicitly says otherwise.

### Google Cloud / Sheets Tips

- Use `gcloud` for Cloud Run, Scheduler, logs, IAM, Secret Manager, and deploys.
- Use `gog` for Google Sheets reads and verification.
- Prefer exact-tab syncs over broad syncs.
- Do not manually edit generated sheets unless Nathan explicitly approves it.
- If a sheet issue likely comes from sync logic, fix the runtime/code path instead of patching the sheet.
- Google Cloud costs are currently just above free-tier levels, so treat larger GCloud spend as a later, roughly 3-month-out cost.

### Security Tips

- Do not expose secrets in docs or chat.
- Keep secrets in Secret Manager or `.env` files with restricted access.
- Put delete operations behind approval.
- Put customer-record changes behind explicit safe workflows.
- Put public or external posts behind clear target confirmation.
- Keep business memory separate from personal memory.

## Cutover Checklist

### Before Cutover

- [ ] Provision server.
- [ ] Enable backups.
- [ ] Install OpenClaw.
- [ ] Create AYA-AI identity.
- [ ] Configure Telegram.
- [ ] Configure Slack.
- [ ] Configure Jobber CLI v3 access.
- [ ] Configure CompanyCam access.
- [ ] Configure GCloud access.
- [ ] Configure business-only memory.
- [ ] Copy/mount canonical KC skills.
- [ ] Confirm no Nathan personal memory is included.

### PP Cutover

- [ ] Dry-run one known one-off PP job.
- [ ] Dry-run one known recurring PP job.
- [ ] Verify CompanyCam user mapping.
- [ ] Verify CompanyCam checklist assignment.
- [ ] Verify Jobber expense creation path.
- [ ] Verify Slack post to `#pp-dispatch-mgmt`.
- [ ] Verify Slack read-back.

### Ops Cutover

- [ ] Verify Slack channel posting.
- [ ] Verify Slack thread reply path.
- [ ] Verify Jobber lookup.
- [ ] Verify CompanyCam read-back.
- [ ] Run unassigned visit audit read-only.

### Finance Cutover

- [ ] Verify margin calculation from quote-side economics.
- [ ] Verify expense lookup.
- [ ] Verify invoice/quote lookup.
- [ ] Verify PP sheet read path.
- [ ] Verify modified quote report references.

### After Cutover

- [ ] Run one full backup restore test.
- [ ] Confirm logs are readable.
- [ ] Confirm Slack/Telegram access boundaries.
- [ ] Confirm no unapproved write paths are open.
- [ ] Document known issues in this project folder.

## Suggested Project Folder Structure

```text
projects/aya-ai-kc-migration/
  README.md
  references-skills-runbook.md
  phase-0-prep.md
  phase-1-pp.md
  phase-1-ops.md
  phase-1-finance.md
  phase-2-sales-marketing-reporting.md
  decisions.md
  risks.md
  cutover-checklist.md
```
