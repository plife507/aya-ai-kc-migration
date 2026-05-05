# KC Slack Channel Ops

## Purpose

Make top-level Slack posting and cross-surface relay predictable from KC topic.

## Canonical target discovery

Find visible sessions first when needed:

```bash
sessions_list(limit=20, activeMinutes=1440, messageLimit=2)
```

Typical bound KC Slack targets:

- top-level channel session:
  - `agent:kc:slack:channel:c08ctuf1t7c`
  - label/display: `slack:#pp-dispatch-mgmt`
- thread session:
  - `agent:kc:slack:channel:c08ctuf1t7c:thread:<threadTs>`

## Top-level posting pattern

Preferred live rule:

- do not treat `TOP>` as active anymore unless Nathan explicitly reinstates it
- default to normal reply behavior for Slack-native mention handling
- make a top-level post only when the user explicitly asks for a top-level/new-channel post
- if the request also involves Jobber writes, costing, or PP interpretation, read `/home/plife507/AYA-CLAW/references/topic-kc.md` and keep Slack delivery as its own step

Preferred pattern from Telegram KC topic or from inside an existing Slack thread:

1. confirm the intended Slack channel target
2. confirm whether the request is for a new top-level channel post or a thread reply
3. if the user says `top level`, `main channel`, `main PP channel`, or equivalent from inside a thread, treat the final post as channel-root delivery, not a thread reply
4. if Jobber work is part of the request, finish the Jobber read/write step first through the proper Jobber skill or wrapper
5. build the exact final Slack body in KC house format
6. use the real Slack outbound/message lane with that exact final post body; if that lane inherits thread context, use Slack `chat.postMessage` directly with only `channel` and no `thread_ts`
7. verify the actual Slack response/read-back shows no `thread_ts` before reporting a top-level post as sent
8. if anything is ambiguous, inspect session history only as supporting evidence, not as proof by itself

Stay in one canonical execution lane during the Slack task unless there is a real reason to switch.
Do not treat session transcript activity as a substitute for actual Slack channel evidence.

Recommended operator understanding:

```text
Post a new top-level margin review for job 20390 in #pp-dispatch-mgmt
```

This should be interpreted as:
- new top-level post
- not a thread reply
- no extra wrapper commentary unless requested
- use the actual Slack surface, not inter-session relay alone

## Linked Jobber formatting standard

For KC Slack posts, prefer a linked Job line when the Jobber ids are known.

Standard format:

```text
Job: <https://secure.getjobber.com/clients/<clientId>|Client Name> - <https://secure.getjobber.com/work_orders/<jobId>|Job #12345>
```

Use this as the default for:
- margin review posts
- info-only posts
- custom notes posts

If ids are not yet known, fall back to plain text rather than guessing URLs.

## CompanyCam checklist selection

Use `Ops: Revisit > Task Guide` only when Nathan explicitly says `revisit`. If he does not say revisit, use the normal checklist for the job type.

For recurring or revisit CompanyCam work, use the existing matching project/album. Do not create a new CompanyCam project unless Nathan explicitly asks for a new album/project. If an accidental empty duplicate is created, first apply the checklist/users to the correct existing project, then use `companycam projects merge --source-project-id <duplicate> --target-project-id <keeper> --archive-empty-source` to archive the duplicate. Non-empty duplicates must be merged in the CompanyCam web app so photos/files/reports/pages transfer correctly.

## Recurring job info-note standard

For recurring jobs where Nathan wants an info-only post rather than a full P&L block, keep the main body lean:

- `Job`
- `Scope`
- `Location`
- `Notes`

Put the recurring economics inside `Notes:`.

For recurring notes, treat the numbers Nathan types in the note as the per-visit calculator inputs.
Do not substitute Jobber quote totals for the note-level margin unless Nathan explicitly asks for quote-side economics.

Preferred format:

```text
Notes: Recurring <name> (Sub Pay: $X - Sale Price: $Y - Margin: $Z / NN.NN%)
```

Example:

```text
Notes: Recurring Jason (Sub Pay: $85 - Sale Price: $140 - Margin: $55.00 / 39.29%)
```

## Important caution

A Slack channel session historically could carry a stale `deliveryContext.threadId` from the last active thread.
The KC channel session was cleaned on 2026-04-26 and the runtime merge path now strips inherited thread state when an explicit channel target has no thread.
Still verify the actual Slack send/read-back for top-level posts, because transcript activity is not delivery proof.

Separate hard rule:
- `sessions_send` is not a Slack post path by itself
- it is inter-session relay only
- transcript echoes from that path are not delivery confirmation

## Verification posture

After timeout or ambiguous behavior, inspect recent target-session history.
You are looking for one of these:

- a final assistant message indicating the post was sent
- a direct surface echo/confirmation
- evidence the session got stuck in tool recursion or self-send

If you do not have positive evidence, report:
- forwarded to Slack-bound session
- top-level delivery unconfirmed

If the real Slack send path confirms success, then and only then report:
- sent

## Clean composite pattern

For combined requests like `job 20415 add expense for Vortex and post with margin to channel`, keep the lanes explicit:

1. resolve the exact job if needed
2. Slack operator decides target surface and delivery mode
3. Jobber operator performs the expense write
4. KC costing rules shape the final P&L body
5. Slack operator sends the final body and reports confirmed result

Do not let a mixed request drift into repeated exploratory queries once the job is already resolved well enough to act.

If Nathan asks for a review based on "job messages we posted," use the actual Slack channel messages as the source set, not inter-session transcript echoes and not only Aya-authored margin blocks.

## Suggested future hardening

1. add a dedicated KC posting lane that is not thread-sticky
2. add an explicit top-level-vs-thread command contract
3. add a local runbook for "post body only" vs "thread reply" patterns
4. if needed later, add a helper script/reference for session targeting and delivery confirmation language
