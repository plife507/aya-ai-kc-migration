# PP Job Workflow

Use this for repeated KC Preferred Partner job stubs that need Jobber expense, CompanyCam setup, margin math, and a Slack post to `#pp-dispatch-mgmt`.

## Lean Morning Batch Mode

For Nathan's morning PP job stub sequence, keep the workflow tight and avoid broad context loading.

If Nathan starts a message with `PPFLOW`, that is the explicit command to use this lane. Parse the fields from the message, run the dry-run/apply wrapper path, and do not gather broad context.

Preferred command shape:

```text
PPFLOW
Job #20494
Sub: Jason
Pay: 500
Date: 4/28
Kind: one off
Checklist: subcon
Note: optional Slack note
```

Supported optional fields:

- `CompanyCam Project: <id>`: use that album directly.
- `Checklist: revisit`: use `Ops: Revisit > Task Guide`.
- `Job Info`: info-only post; skip Jobber expense and margin fields.

Use the stub as the source of truth, then do only the minimum checks needed for that job:

- resolve the exact Jobber job from the job number
- check/update the one subcontractor expense for the requested visit date and pay
- use the reviewed PP CompanyCam assignment mapping or an explicit CompanyCam user id
- resolve the CompanyCam project from Jobber's CompanyCam custom field first when present
- use a known CompanyCam project id when Nathan provides one
- reuse existing CompanyCam albums whenever possible; if the Jobber custom field is empty and no confident album is found, surface the no-match/candidate result and ask before creating anything
- create a new CompanyCam project only when Nathan explicitly approves it in the thread or passes that intent through `--create-companycam-project`
- send or edit the single intended `#pp-dispatch-mgmt` Slack post, then verify delivery/read-back
- report back with a short result-only confirmation

Do not reread broad memory, transcript history, or unrelated docs for each stub. Only expand context when the job is ambiguous, a write fails, or Nathan asks for diagnosis.

## Dry Run

```bash
python3 /home/plife507/AYA-CLAW/skills/kc-pp-job-costing/scripts/pp_job_workflow.py \
  20491 \
  --sub "Shamus WP - Washpros" \
  --pay 200 \
  --date 4/27 \
  --kind One-Off
```

The dry run:

- resolves the exact Jobber job
- resolves the PP identity from the explicit CompanyCam assignment registry
- reads quote-side total and discount
- checks existing Jobber expenses using the resolved expense vendor label
- reads Jobber's CompanyCam custom field before falling back to CompanyCam search
- plans CompanyCam project/checklist/user assignment, including multi-user PP assignments
- computes margin
- emits `slack.body` for the real `#pp-dispatch-mgmt` Slack send lane

## Apply

After the dry-run output is correct:

```bash
python3 /home/plife507/AYA-CLAW/skills/kc-pp-job-costing/scripts/pp_job_workflow.py \
  <jobNumber> \
  --sub "Sub Name" \
  --pay <amount> \
  --date <date> \
  --kind One-Off \
  --apply
```

`--apply` creates a missing Jobber subcontractor expense and applies CompanyCam checklist/user writes. CompanyCam creation is blocked unless `--create-companycam-project` is passed; by default the wrapper uses `--companycam-project-id`, reads Jobber's CompanyCam custom field, matches one safe existing album, or stops for review. It rejects ambiguous, truncated, weak, jobwalk, estimate, quote, or bid-style project matches. It still does not post to Slack. Send the emitted `slack.body` through OpenClaw's Slack message lane and verify the channel read-back.

## Useful Flags

- `--job-info --note "Note text"`: prepare an info-only Slack post, skip Jobber expense, and omit margin fields.
- `--companycam-project-id <id>`: use a known existing CompanyCam project/album; prefer this for recurring jobs and recovery.
- `--create-companycam-project`: allow a new CompanyCam album only after confirming no existing album should be reused; this only proceeds when the match lane finds no existing project.
- `--force-new-checklist`: create a fresh checklist instance even when that template is already present; use this for recurring visit checklists.
- `--companycam-user-id <id>`: force the CompanyCam assignee by exact reviewed id. Comma- or space-separated IDs are allowed for multi-user PP assignments.
- `--companycam-user-query "Name"`: dry-run discovery helper only. It is blocked with `--apply`; add the reviewed mapping to `/home/plife507/AYA-CLAW/skills/kc-pp-job-costing/references/pp-companycam-assignments.json` or pass `--companycam-user-id` before live writes.
- `--note "Note text"`: append `Notes:` to a normal costing post; required with `--job-info`.
- `--sale <amount>`: override the sale amount used for costing/Slack, useful when a recurring Jobber quote total covers more than the single visit price Nathan provides.
- `--skip-expense`: do only CompanyCam and Slack body prep.
- `--skip-companycam`: do only Jobber expense check/write and Slack body prep.
- `--checklist-template-id <id>`: override checklist selection. By default, `--kind Recurring` uses `52548` / `Ops: PW Comm> General/Misc Jobs`; other PP setup uses `61791` / `Ops: Subcon > Task Guide`.

## Info-Only Job Updates

For stubs like `Job Info` with no sub pay, do not create a fake `$0` expense and do not post margin fields. CompanyCam assignment still needs a reviewed registry mapping or explicit user id; use `--skip-companycam` only when the update is Slack-only.

```bash
python3 /home/plife507/AYA-CLAW/skills/kc-pp-job-costing/scripts/pp_job_workflow.py \
  20443 \
  --sub "Jason" \
  --date 4/27 \
  --job-info \
  --note "Sub on site today for Demo"
```

Use `--apply` after the dry run is clean to apply CompanyCam setup/user assignment. The script still emits `slack.body` for real Slack posting and read-back.

## Recurring Jobs

For recurring jobs with a known CompanyCam project, pass the project id directly so the wrapper does not create a duplicate recurring album:

```bash
python3 /home/plife507/AYA-CLAW/skills/kc-pp-job-costing/scripts/pp_job_workflow.py \
  19372 \
  --sub "Jason" \
  --pay 85 \
  --sale 140 \
  --date 4/27 \
  --kind Recurring \
  --companycam-project-id 97853136 \
  --force-new-checklist \
  --note "CC checklist: Ops: PW Comm> General/Misc Jobs."
```

## Slack Finish

Post `slack.body` to `#pp-dispatch-mgmt` / `C08CTUF1T7C` and read back the channel before reporting done. Do not use this PP workflow for other Slack channels.
