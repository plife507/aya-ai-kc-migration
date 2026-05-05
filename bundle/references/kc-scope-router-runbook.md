# KC Scope Router Runbook

Purpose: route KC-topic requests into the correct scope before downstream Slack or Jobber actions.

Read `/home/plife507/AYA-CLAW/references/topic-kc.md` when a request mixes thread scope, Jobber action, costing, or Slack delivery so the lane order stays explicit.

## Runtime model

There are three practical request modes:

1. `job_info`
- for job lookup and job context requests
- does not require Slack thread binding

2. `slack_reply`
- for exact Slack thread reply or thread-context reading
- requires thread scope

3. `thread_to_jobber`
- for actions that connect a Slack thread to a Jobber job or note workflow
- requires thread scope and usually job scope too

Top-level channel posting is a separate concern.
Do not force it through the thread resolver/router model.
Use the bound Slack channel session plus `kc-slack-channel-operator` guidance for:
- top-level posts into `#pp-dispatch-mgmt`
- cross-surface Telegram ↔ Slack relay behavior
- sent-vs-forwarded confirmation language

## Scripts

Resolver:
- `/home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py`

Router:
- `/home/plife507/AYA-CLAW/scripts/kc_scope_router.py`

## Persisted state

Thread lock:
- `/home/plife507/AYA-CLAW/state/kc-slack-scope-lock.json`

Job lock:
- `/home/plife507/AYA-CLAW/state/kc-job-scope-lock.json`

Thread registry:
- `/home/plife507/AYA-CLAW/state/slack-thread-registry.json`

## Commands

Job info route:
```bash
python3 /home/plife507/AYA-CLAW/scripts/kc_scope_router.py route job_info "what is going on with job 20283"
```

Slack thread reply route:
```bash
python3 /home/plife507/AYA-CLAW/scripts/kc_scope_router.py route slack_reply "steve message" --channel '#test' --include-archived
```

Thread to Jobber route:
```bash
python3 /home/plife507/AYA-CLAW/scripts/kc_scope_router.py route thread_to_jobber "20283 reschedule" --channel '#test' --include-archived
```

Show active locks:
```bash
python3 /home/plife507/AYA-CLAW/scripts/kc_scope_router.py show
```

## Current tested behavior

- `job_info` correctly extracts explicit job number references and writes a job scope lock.
- `slack_reply` resolves archived thread references through transcript-backed thread search.
- `thread_to_jobber` resolves a thread and carries the bound job number in the thread scope lock when discoverable.

## Safety expectations

- Keep KC routing professional and closure-focused: the result should end in done, blocked, needs decision, or needs verification.
- If routing is blocked, report the blocker as an investigation item: exact blocker, known matches, missing scope, risk of guessing, and next verification.
- Do not force job-only questions through Slack thread binding.
- Do not force thread-only questions through Jobber lookup unless the action actually needs it.
- Do not treat top-level channel posting as if it were thread routing.
- For write actions, exact scope should be known before execution.
- If a match is ambiguous, treat that as a confirmation step rather than pretending confidence.
- For mixed thread-plus-Jobber work, resolve the exact Slack thread first, then resolve the exact job, then perform the requested action through the canonical Jobber lane.

## Public-channel test focus

For tonight's PP testing, confirm:
1. job info requests resolve cleanly from KC topic
2. thread references resolve to the correct Slack thread
3. thread-plus-job requests bind both cleanly enough for note workflows
4. no stale thread carryover leaks into top-level channel actions
