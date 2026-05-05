# PP Human-In-Loop Workflow

Use this reference for Nathan's short KC PP job stubs in Telegram or Slack.

## Decision

Do not split `scripts/pp_job_workflow.py` yet. The current wrapper should stay as the orchestrator because it keeps Jobber, CompanyCam, costing, and Slack-body generation in one previewable dry-run. Split only when a sub-step needs independent reuse across non-PP workflows, or when the script becomes hard to test because a bug in one lane blocks validating another lane.

The correct boundary today is:

- deterministic helper scripts for fragile writes
- skill rules for human shorthand and approval gates
- real Slack delivery outside the workflow script

## Normal PP Job Stub

When Nathan gives a compact job block with job number, PP/sub, pay, date, checklist/type, and note, treat it as intent to execute the full PP setup:

1. Run `pp_job_workflow.py` in dry-run mode.
2. Confirm the dry-run resolved the exact Jobber job, quote-side sale, PP registry mapping, CompanyCam project, checklist, and Slack body.
3. If all targets are exact and no create/ambiguous action is required, run the same command with `--apply`.
4. Send the emitted `slack.body` through the real Slack message lane to `#pp-dispatch-mgmt`.
5. Reply with a terse done state.

Use the reviewed PP registry label in Jobber and Slack output even when Nathan's shorthand is looser, for example `Washpro - Shamus` should resolve to `Shamus WP - Washpros` when the alias is reviewed.

## `PPFLOW` Chat Command

When Nathan starts a message with `PPFLOW`, treat it as an explicit command to invoke the normal PP job workflow with minimal context.

Accepted shape:

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

Do not load broad memory, old conversation history, unrelated docs, or old Slack context for a `PPFLOW` job. Use only the command fields, the PP assignment registry, the workflow wrapper dry-run/apply output, and the specific Jobber/CompanyCam/Slack read-backs required for that job. Expand context only when the dry-run is ambiguous, a service write fails, or Nathan asks for an audit/diagnosis.

## Human Gates

Proceed after dry-run without asking when all are true:

- exact Jobber job number match
- one reviewed PP assignment or explicit CompanyCam user id
- existing CompanyCam project from explicit id, Jobber custom field, or one safe address match
- normal checklist selection is clear from Nathan's wording
- no new CompanyCam project is needed
- Slack target is the standard PP channel

Stop and ask Nathan when any of these appear:

- no reviewed PP assignment and no explicit CompanyCam user id
- multiple possible CompanyCam projects or a weak/jobwalk/estimate match
- CompanyCam project creation would be required
- checklist type is unclear or conflicts with wording
- user intent conflicts, such as `job info only` plus a requested P&L block
- the request would edit/delete/merge records rather than create the expected expense/checklist/assignment

## Checklist Selection

- `revisit` means `Ops: Revisit > Task Guide`.
- `Recurring` PP jobs mean `Ops: PW Comm> General/Misc Jobs` unless Nathan explicitly says otherwise. Use a fresh checklist for each recurring visit when the same long-running CompanyCam project is reused.
- `Sub Con`, `subcon`, `subbed`, or normal subcontractor PP setup means `Ops: Subcon > Task Guide`.
- If neither applies, use the normal PP wrapper default only when the rest of the job stub clearly describes a subcontractor setup.

## Info-Only Then Expense Correction

If Nathan first asks for `job info only`, do not create an expense or show P&L/margin.

If he later says to add an expense but not calculate P&L:

1. Add only the Jobber expense using the subcontractor expense wrapper.
2. Edit or append the existing Slack note to mention the expense.
3. Do not convert the post into a P&L block.
4. Do not add `Sale`, `Sub Pay`, or `Margin` fields.

This is a correction lane, not a costing lane.

## Output Discipline

For Telegram completion replies, report the operational result only:

```text
Done. Added the $X Jobber subcontractor expense, applied/assigned CompanyCam as needed, and posted/edited #pp-dispatch-mgmt.
```

Do not expose dry-run JSON, session ids, or internal routing details unless Nathan asks for an audit.
