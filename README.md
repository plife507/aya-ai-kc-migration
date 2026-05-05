# AYA-AI KC Migration Plan

## Quick Start For New System

```bash
git clone https://github.com/plife507/aya-ai-kc-migration.git
cd aya-ai-kc-migration
make validate
```

Use `ingestion-manifest.json` as the machine-readable source of truth for what to ingest. Use `ingestion-plan.md` for operator guidance, chunking rules, metadata tags, and secret rehydration boundaries.

Secrets are intentionally not included. Rehydrate credentials separately through the target OpenClaw secret system, restricted files, or Secret Manager.

## 1. Goal

Migrate KC Power Clean's current workflows into a dedicated AYA-AI system.

AYA-AI will support the business through Telegram and Slack, with department modules for:

- HQ
- PP
- Ops
- Finance
- Sales
- Marketing
- Reporting / Dashboards

Phase 1 will focus on the workflows already producing operational value.

## 2. Target System

AYA-AI will run as one managed OpenClaw system.

Department leads will access AYA-AI through Telegram. Employees will be able to ask AYA-AI questions from approved Slack channels. AYA-AI can push reports, alerts, and workflow updates into Slack when needed.

The system should keep business memory separate from Nathan's personal Aya memory.

## 3. Phase 1 Rollout

### HQ

Purpose:

- Owner / VP visibility
- Approval routing
- Department routing
- System oversight
- High-level reporting

Migrate:

- AYA-AI proposal and operating model
- Telegram access for leadership
- Slack report delivery rules
- Approval gates for external posts, expenses, deletes, and customer-record changes

Target result:

- HQ becomes the command center for AYA-AI.

### PP

Purpose:

- Preferred Partner job workflow
- Subcontractor expenses
- CompanyCam setup
- Slack dispatch posts
- Margin reporting

Migrate:

- `PPFLOW` command
- Jobber job lookup
- Jobber subcontractor expense creation
- CompanyCam project lookup / reuse / creation approval
- CompanyCam checklist assignment
- CompanyCam user assignment
- Slack posting to `#pp-dispatch-mgmt`
- Margin calculation
- Recurring PP job handling

Current key rules:

- Use Jobber as source of truth for job identity.
- Use quote-side economics for margin.
- Use reviewed CompanyCam user mappings.
- Reuse existing CompanyCam projects when possible.
- Do not create CompanyCam projects unless approved or clearly requested.
- Verify Slack delivery after posting.

Target result:

- PP jobs can be handled from a clean command flow: job, sub, pay, date, checklist, and notes.

### Ops

Purpose:

- Dispatch support
- Crew coordination
- Jobber / CompanyCam operational checks
- Slack channel support

Migrate:

- Slack channel operations
- Slack thread replies
- Dispatch channel routing
- CompanyCam verification
- Jobber job lookups
- Unassigned visit audits
- Crew assignment review workflows

Current Slack channels to support:

- `#pp-dispatch-mgmt`
- `#ops-frontstage`
- `#dispatch-pm`

Target result:

- Ops can ask AYA-AI about jobs, crews, assignments, checklists, and dispatch status from Telegram or Slack.

### Finance

Purpose:

- Expense visibility
- Margin checks
- Invoice / quote review
- PP profitability
- Financial reporting support

Migrate:

- PP margin math
- Subcontractor expense tracking
- Jobber expense lookup
- Quote-side discount handling
- Modified quote reports
- PP sheet margin outputs
- Finance-facing summaries

Current finance rules:

- Do not rely on Slack text alone for costing.
- Verify sale basis from Jobber or PP sheet.
- Include discounts in profitability.
- Separate quoted sale, invoiced sale, sub pay, margin dollars, and margin percent.

Target result:

- Finance can ask AYA-AI for job profitability, margin checks, sub pay totals, and invoice/expense review.

## 4. Phase 2 Rollout

### Sales

Add later after Phase 1 is stable.

Planned scope:

- Lead tracking
- Estimate follow-ups
- Quote status
- Sales pipeline summaries
- Jobber sales lookup
- Missed opportunity reports

### Marketing

Add later after Phase 1 is stable.

Planned scope:

- Reviews
- Photos
- CompanyCam content discovery
- Campaign notes
- Website / social content support
- Before-and-after job media workflows

### Reporting / Dashboards

Add later after Phase 1 is stable.

Planned scope:

- Daily summaries
- Weekly summaries
- KPI dashboards
- PP performance reports
- Ops workload reports
- Finance margin reports
- Sales pipeline reports

Google Cloud costs are currently just above free-tier levels, so Reporting / Dashboards should be treated as a later cost, likely around 3 months out.

## 5. Current Systems To Migrate

### OpenClaw / Aya

Current use:

- Telegram group workflows
- Slack coordination
- Jobber / CompanyCam / Google Cloud support
- PP workflow execution

Migration action:

- Create a dedicated KC AYA-AI instance.
- Keep KC business memory separate.
- Move reusable KC workflows into AYA-AI skills/modules.
- Do not import Nathan personal memory.

### Jobber

Current use:

- Job lookup
- Client/job identity
- Expenses
- Notes
- Quotes
- Invoices
- Unassigned visit audits

Migration action:

- Connect AYA-AI to Jobber CLI v3.
- Preserve OAuth/token handling.
- Keep writes gated.
- Build Phase 1 Jobber tools around PP, Ops, and Finance.

### CompanyCam

Current use:

- Project lookup
- Project creation when approved
- Checklist assignment
- User assignment
- Project verification

Migration action:

- Move PP CompanyCam assignment registry into AYA-AI.
- Preserve checklist rules.
- Build verification read-back after every CompanyCam write.
- Keep project creation guarded.

### Slack

Current use:

- PP dispatch posts
- Ops channel posts
- Thread replies
- Reports and alerts

Migration action:

- Connect AYA-AI to KC Slack.
- Define approved channels.
- Allow employee questions from approved Slack channels.
- Allow AYA-AI to push approved reports and alerts.
- Keep delivery confirmation required for important posts.

### Google Cloud / Google Workspace

Current use:

- KC PP Sync Cloud Run
- Scheduler jobs
- Google Sheets sync
- Dashboard outputs
- Logs and runtime checks

Migration action:

- Keep existing GCloud services running.
- Connect AYA-AI to monitor and operate them.
- Treat GCloud as low cost at launch.
- Expand Reporting / Dashboards in Phase 2.

### KC PP Sync Sheet

Current use:

- Month tabs
- Recurring tabs
- Dashboard
- Command / Log tabs
- PP sheet sync from Jobber / HeyPros

Migration action:

- AYA-AI should read sheet outputs for reporting and validation.
- Keep Cloud Run as the sync engine.
- Use exact-tab sync commands when needed.
- Avoid manual sheet edits unless explicitly approved.

## 6. Migration Phases

### Phase 0: Prep

- Confirm server provider and size.
- Create new AYA-AI identity.
- Confirm Telegram group/channel access.
- Confirm Slack app/channel access.
- Confirm Jobber, CompanyCam, and Google Cloud credentials.
- Create backup plan before migration.

Deliverable:

- AYA-AI server ready.
- Secure access through SSH / Cursor / OpenClaw.

### Phase 1A: Base System

- Install OpenClaw.
- Configure AYA-AI identity.
- Configure Telegram.
- Configure Slack.
- Set up business-only memory.
- Set up logs and backups.
- Create department module structure: HQ, PP, Ops, and Finance.

Deliverable:

- AYA-AI can receive Telegram and Slack requests.

### Phase 1B: PP Workflow Migration

- Move `PPFLOW` workflow.
- Move PP CompanyCam assignment mapping.
- Move PP recurring job references.
- Connect Jobber expense workflow.
- Connect CompanyCam workflow.
- Connect Slack `#pp-dispatch-mgmt` posting.
- Test with dry runs first.
- Test one controlled live job.

Deliverable:

- AYA-AI can complete PP workflow end-to-end.

### Phase 1C: Ops Migration

- Add Slack channel operations.
- Add Jobber lookup support.
- Add CompanyCam verification support.
- Add unassigned visit audit support.
- Add dispatch summary support.

Deliverable:

- Ops can use AYA-AI for dispatch and job coordination.

### Phase 1D: Finance Migration

- Add margin review.
- Add expense review.
- Add quote/invoice lookup.
- Add PP profitability summaries.
- Add modified quote report review.

Deliverable:

- Finance can ask AYA-AI for job and PP financial visibility.

### Phase 2: Growth Modules

Add after Phase 1 is stable:

- Sales
- Marketing
- Reporting / Dashboards

Deliverable:

- AYA-AI expands from operating assistant into full business intelligence assistant.

## 7. Hosting Plan

Recommended:

- Provider: Vultr
- Server: 8 vCPU / 16 GB RAM
- Backups enabled
- Ubuntu 24.04 LTS
- SSH access
- Cursor access
- OpenClaw administration

Estimated launch budget:

- OpenAI Pro: $200
- Vultr hosting with backups: about $115
- Google Cloud: minimal at launch
- Backup/storage extras: $10-$20

Estimated launch total:

- About $325-$350/month

Estimated later total with more GCloud usage:

- About $365-$415/month

## 8. Backup Plan

Use three backup layers:

1. Vultr automatic backups
2. Snapshots before major upgrades
3. Nightly encrypted off-box backups to Google Cloud Storage

Back up:

- OpenClaw config
- AYA-AI memory
- KC workflow docs
- Skills/modules
- Environment templates
- Service configs
- Logs needed for audit

Do not store raw secrets in normal documentation.

## 9. Security Rules

- Department leads use Telegram.
- Employees use approved Slack channels.
- AYA-AI can post to Slack only through approved workflows.
- Writes to Jobber require explicit safe workflow.
- CompanyCam project creation is guarded.
- Deletions require approval.
- Financial and customer data should stay inside approved systems.
- Personal Nathan memory does not migrate into AYA-AI.

## 10. Success Criteria

AYA-AI migration is successful when:

- HQ can route requests through Telegram.
- Employees can ask approved questions in Slack.
- PP workflow works end-to-end.
- Jobber expenses can be created safely.
- CompanyCam checklists/users are verified.
- Slack posts are confirmed by read-back.
- Ops can check dispatch/job status.
- Finance can review margin and expenses.
- Backups are running.
- Logs are available.
- No personal memory is mixed into the KC business system.

## 11. Recommendation

Start with one AYA-AI OpenClaw system.

Launch Phase 1 with:

- HQ
- PP
- Ops
- Finance

Add Phase 2 later:

- Sales
- Marketing
- Reporting / Dashboards

This gives KC Power Clean the highest value first, keeps the launch cost controlled, and avoids overbuilding before the core workflows are stable.

## Supporting Documents

- [References, Skills, Tips, And Tricks](references-skills-runbook.md)
- [Efficient Ingestion Plan](ingestion-plan.md)
- [Machine-Readable Ingestion Manifest](ingestion-manifest.json)
