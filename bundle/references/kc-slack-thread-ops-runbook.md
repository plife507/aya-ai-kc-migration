# KC Slack Thread Ops Runbook

Purpose: practical operator runbook for using the local Slack thread resolver from KC topic before and during PP cutover.

## Resolver script

Path:
- `/home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py`

Registry output:
- `/home/plife507/AYA-CLAW/state/slack-thread-registry.json`

Scope lock output:
- `/home/plife507/AYA-CLAW/state/kc-slack-scope-lock.json`

## What it does

- reads the active OpenClaw session store
- finds Slack thread sessions
- extracts thread metadata from session entries and transcripts
- builds a local searchable registry
- supports natural-reference search from KC topic workflows
- can materialize an exact scope lock for downstream Slack or Jobber work

## Core commands

Refresh registry:
```bash
python3 /home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py refresh --include-archived
```

Search by natural phrase:
```bash
python3 /home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py search "steve thread" --channel '#test' --include-archived
```

Search by job number:
```bash
python3 /home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py search "20283 reschedule" --channel '#test' --include-archived
```

Resolve into a candidate scope lock:
```bash
python3 /home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py resolve "20283 reschedule" --channel '#test' --action jobber_write --include-archived
```

Resolve and persist only when clearly matched:
```bash
python3 /home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py resolve "20283 reschedule" --channel '#test' --action jobber_write --include-archived --write-lock
```

Bind a known exact thread:
```bash
python3 /home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py bind 1776637220.126489 --action jobber_write --job-number 20283 --include-archived
```

Show exact thread metadata:
```bash
python3 /home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py show 1776637220.126489 --include-archived
```

Show current scope lock:
```bash
python3 /home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py show-lock
```

Clear current scope lock:
```bash
python3 /home/plife507/AYA-CLAW/scripts/slack_thread_resolver.py clear-lock
```

## Intended KC topic use

From KC topic, Nathan should be able to refer to a thread naturally.
Aya should:
1. refresh/search registry
2. resolve to the best candidate set
3. auto-lock only when one candidate is clearly dominant
4. ask for confirmation when ambiguous
5. bind execution to exact `threadTs`
6. end with a clear state: resolved, blocked, needs confirmation, or ready for the next action

## Scope lock contract

The persisted scope lock records:
- exact Slack channel id
- exact Slack thread ts
- exact session key when known
- transcript path
- intended action type
- bound job number if known or inferable
- whether confirmation was still required

The lock is a runtime aid, not authority by itself.

## Safety rule

The resolver helps find and bind the exact thread.
It does not itself authorize writes.
Before Jobber note writes or Slack escalations, also confirm:
- exact job identity
- exact thread
- requested action
- approval state if the action needs approval

If thread resolution is blocked, surface the investigation item instead of guessing:
- blocker
- known candidates
- missing identifier or context
- risk of replying to the wrong thread
- next verification

## Current cutover intent

Use this for:
- thread discovery
- thread confirmation
- exact thread binding
- keeping tabs on active Slack work items
- reducing ambiguity before PP channel cutover

Not yet sufficient by itself for:
- automatic Slack thread routing decisions inside OpenClaw core
- autonomous Jobber writes without normal approval rules
