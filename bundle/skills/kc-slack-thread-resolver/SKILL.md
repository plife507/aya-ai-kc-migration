---
name: kc-slack-thread-resolver
description: Resolve KC Slack threads from natural-language references by searching OpenClaw Slack session state and transcript-backed thread registry. Use when Nathan refers to a Slack thread loosely from KC topic, when exact thread binding is needed before thread replies or Jobber writes, or when active Slack test/PP threads must be discovered, confirmed, and reused safely.
---

# KC Slack Thread Resolver

Use this skill when KC-topic Aya needs to find an exact Slack thread from a natural reference.

For top-level channel posting, cross-surface relay behavior, or sent-vs-forwarded confirmation on the bound KC Slack channel, use `kc-slack-channel-operator` instead.
For mixed thread-plus-Jobber tasks, also read `/home/plife507/AYA-CLAW/references/topic-kc.md` so the lane order stays explicit.

## Purpose

Convert natural references like:
- "the 20283 reschedule thread"
- "that Steve thread"
- "the latest profitability thread in #test"
- "the thread where I said I don't see your steve message"

into an exact Slack thread binding:
- channel id
- channel name if known
- thread ts
- session key if available
- transcript-backed context preview

## Resolver runtime

Script:
- `/home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py`

Registry output:
- `/home/plife507/AYA-CLAW/state/slack-thread-registry.json`

Runbook:
- `/home/plife507/AYA-CLAW/references/kc-slack-thread-ops-runbook.md`

## Default operating flow

1. Refresh/search the local Slack thread registry.
2. If one strong match exists, state the resolved thread clearly.
3. If multiple plausible matches exist, show the top candidates briefly and ask Nathan to pick.
4. Before meaningful execution, bind to the exact `threadTs`.
5. For Jobber writes, also resolve the exact job before acting.
6. End with a clear state: resolved, blocked, needs confirmation, or ready for the next action.

## Core commands

Refresh:
```bash
python3 /home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py refresh --include-archived
```

Search:
```bash
python3 /home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py search "20283 reschedule" --channel '#test' --include-archived
```

Show exact thread:
```bash
python3 /home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py show 1776637220.126489 --include-archived
```

## Interpretation rules

- Prefer exact job number matches when present.
- Prefer exact phrase matches from thread previews.
- Use recency as a tiebreaker, not as sole authority.
- Treat transcript-backed archived threads as valid discovery anchors.
- Do not guess across multiple plausible candidates.

## Safety rule

The resolver finds the exact Slack thread.
It does not by itself authorize a write.

Before any write or irreversible action, confirm:
- exact Slack thread
- exact job identity if relevant
- requested action

## Good answer shape

If the match is clear:
- "I found the #test thread for job 20283, thread 1776637220.126489. Using that one."

If ambiguous:
- "I found two likely threads in #test: 20283 reschedule and 20408 profitability. Which one do you want?"

If blocked:
- `Blocker:` why the thread cannot be bound safely
- `Known:` the strongest candidate facts
- `Missing:` the identifier or context needed
- `Risk:` what could go wrong if guessed
- `Next:` the verification step

## Current cutover intent

Use this skill for PP cutover prep so KC topic can:
- keep tabs on real Slack threads
- search by natural reference
- confirm exact thread binding
- reduce cross-thread mistakes before Jobber or Slack actions
