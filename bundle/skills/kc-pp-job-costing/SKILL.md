---
name: kc-pp-job-costing
description: Compute and present KC Preferred Partner job costing for one or more jobs. Use when Nathan wants sale, sub pay, margin dollars, or margin percent for KC PP jobs, when building Slack-ready costing posts, or when validating whether profitability should come from quote-side economics, discounts, invoiced amounts, or sheet outputs. Prefer this skill before drafting PP costing posts or answering margin/profitability questions.
---

# KC PP Job Costing

Use this skill when the task is to compute, validate, or format KC Preferred Partner job costing.

## Core rules

- Do not guess profitability from one surface if another surface is required to explain it.
- Treat quote-side economics as part of profitability, including discounts.
- Distinguish clearly between:
  - quoted sale
  - invoiced sale
  - subcontractor pay
  - margin dollars
  - margin percent
- If a requested output needs a single authoritative number, say which source produced it.
- If sheet output and Jobber context disagree, report the mismatch instead of smoothing it over.
- Present KC costing in a polished executive-assistant style: concise, useful, clear about verified vs inferred data, and firm about missing inputs.

## Source posture

Use these lanes in order:

1. `kc-pp-sync-operator`
- use when you need the current PP sheet row, dashboard view, or existing margin output

2. `jobber-cli-v3-operator`
- use when you need official Jobber job, quote, invoice, note, or expense context

3. local references
- read `references/costing-rules.md` for calculation and formatting rules

Do not rely on Slack text alone for costing.
If the request mixes costing with Slack delivery or Jobber writes, read `/home/plife507/AYA-CLAW/references/topic-kc.md` and keep costing as its own lane rather than folding it into delivery or mutation work.

## Costing workflow

1. Resolve the exact job
- confirm the job number
- identify client/job title if needed for display

2. Determine the sale basis
- prefer quote-side economics when the question is about profitability or margin
- include discounts when present
- if only invoiced totals are available, say so explicitly

3. Determine subcontractor pay
- use the PP sheet or confirmed Jobber expense/payment context
- for the first version, prefer the Jobber line as the subcontractor source of truth when available
- if multiple subs exist, total them and say that it is combined sub pay
- do not collapse multiple subcontractor names into one name
- if exactly one Jobber line/subcontractor is confirmed, display that one name
- if multiple subcontractors are confirmed, list them explicitly when the output lane supports it
- for KC Slack house format:
  - single-sub post uses `Sub: <name>`
  - multi-sub post uses `Subs:` with one line per subcontractor and combined `Sub Pay`

4. Compute margin
- `margin_dollars = sale - sub_pay`
- `margin_percent = margin_dollars / sale * 100`
- if sale is zero or missing, do not fabricate a margin

5. Format the result for the requested lane
- plain answer
- Slack-ready block
- comparison or validation note

## Slack post posture

When preparing a Slack-ready costing post:

- keep the field order stable
- use money formatting with commas and 2 decimals
- use margin percent with 2 decimals
- include the exact job number
- include enough job identity to avoid ambiguity
- when Jobber ids are known, prefer the linked Job line format: `Job: <client-url|Client Name> - <job-url|Job #12345>`
- if the job has one subcontractor, use `Sub: <name>`
- if the job has multiple subcontractors, use combined `Sub Pay`, then `Subs:` with one line per sub
- margin math for the standard P&L shape is based on quote-side sale, discount, total, and subcontractor pay

## Repeatable PP Job Setup Command

For Nathan's recurring `Slack + CompanyCam + expense` PP job stubs, prefer the workflow wrapper before doing manual one-off command chains:

### Chat trigger

When Nathan starts a Telegram/Slack message with `PPFLOW`, treat it as an explicit request to run this lean PP workflow and avoid broad context gathering.

Preferred chat format:

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

Optional fields:

- `CompanyCam Project: <id>` when Nathan already knows the album
- `Checklist: revisit` for `Ops: Revisit > Task Guide`
- `Job Info` plus `Note:` for info-only posts with no expense or margin

For `PPFLOW`, use only the job stub, this skill, `references/pp-human-in-loop-workflow.md`, `references/pp-companycam-assignments.json`, the workflow wrapper, and the specific Jobber/CompanyCam/Slack read-backs needed for the named job. Do not load broad conversation history, memory, unrelated docs, or old Slack context unless a match is ambiguous, a write fails, or Nathan asks for diagnosis.

```bash
python3 /home/plife507/AYA-CLAW/skills/kc-pp-job-costing/scripts/pp_job_workflow.py \
  <jobNumber> \
  --sub "Sub Name" \
  --pay 200 \
  --date 4/27 \
  --kind One-Off
```

Default mode is dry-run. It resolves Jobber, resolves the PP identity from `references/pp-companycam-assignments.json`, checks existing expenses using the resolved expense vendor label, applies the reviewed CompanyCam user assignment, computes quote-side margin, and emits the Slack-ready body for `#pp-dispatch-mgmt`. To apply Jobber/CompanyCam writes after the preview is correct, add `--apply`. The script intentionally does not post to Slack; send the emitted `slack.body` through the real Slack message lane to `#pp-dispatch-mgmt` / `C08CTUF1T7C` and verify read-back.

CompanyCam assignment is strict by default. The wrapper must use a reviewed registry mapping or explicit `--companycam-user-id`; it does not infer assignees from `--sub`. Use comma- or space-separated IDs for multi-user PP assignments. `--companycam-user-query` is a dry-run discovery helper only and cannot be used with `--apply`; after discovery, add the mapping to `references/pp-companycam-assignments.json` or pass the exact user id. CompanyCam project matching is also guarded: prefer `--companycam-project-id <id>` for known recurring albums, then use Jobber's CompanyCam custom field when present, then fall back to one safe address match only. It stops on ambiguous, truncated, weak, jobwalk, estimate, quote, or bid-style matches. CompanyCam project creation is blocked by default and only runs from a no-match state; pass `--create-companycam-project` only after confirming a new album is correct. Add `--force-new-checklist` for recurring visits that need a fresh checklist instance even when the same template already exists. Use `--skip-expense` or `--skip-companycam` for partial recovery. For `Job Info` stubs with no sub pay, use `--job-info --note "..."`; this skips Jobber expense creation and emits an info-only Slack body without margin fields. Do not use this PP workflow for other Slack channels.

For morning PP batches, keep the execution lane lean: use the job stub, resolve the exact Jobber job, check/update only the relevant expense, apply CompanyCam only through a reviewed mapping plus known project id or Jobber CompanyCam custom field, and post/edit the one intended `#pp-dispatch-mgmt` message. Do not load broad conversation history, memory, or unrelated docs per job. For CompanyCam work, reuse an existing album whenever possible. If the Jobber custom field is empty and no confident album is found, surface the no-match/candidate result and ask before creating anything. Create a new CompanyCam project only when Nathan explicitly approves it in the thread or passes `--create-companycam-project`.

For the human-in-loop rules behind these compact PP stubs, read `references/pp-human-in-loop-workflow.md`. It defines when to proceed after a clean dry-run, when to stop and ask Nathan, how to handle checklist shorthand, and how to handle an info-only post that later gets an expense without P&L.

## Required cautions

- Profitability questions must inspect quote-side discounts, not just downstream job totals.
- A note write request is not a costing request.
- An expense mutation is not required to answer a costing question.
- If the requested post implies precision but the data is incomplete, say what is missing first.
- Multiple subcontractor costs are a normal edge case; total the pay and present the subcontractor label truthfully.
- For now, prefer the Jobber line/vendor identity over looser sheet or Slack naming when deciding the `Sub` label.

If costing is blocked, surface the investigation item with the missing sale basis, sub pay, discount, job identity, or source mismatch and the next verification step.

## References

- `references/costing-rules.md`
- `references/pp-human-in-loop-workflow.md`
- `/home/plife507/AYA-CLAW/skills/kc-pp-sync-operator/references/sheet-architecture.md`
- `/home/plife507/AYA-CLAW/skills/jobber-cli-v3-operator/SKILL.md`
