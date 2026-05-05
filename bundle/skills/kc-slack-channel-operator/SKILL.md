---
name: kc-slack-channel-operator
description: Operate the bound KC Slack channel from Aya across Telegram and Slack sessions, especially for top-level channel posts, thread replies, cross-surface relays, and sent-vs-forwarded confirmation. Use when Nathan says things like "send it to #pp-dispatch-mgmt", "post this top level in Slack", "reply in that Slack thread", or when channel/thread targeting and delivery confirmation are easy to fumble.
---

# KC Slack Channel Operator

Use this skill to make KC Slack interaction explicit and reliable.

## Core job

Handle four things cleanly:

1. top-level post into the real Slack channel surface
2. reply into an exact Slack thread
3. relay between this KC Telegram topic and the Slack surface
4. report delivery truthfully: sent, forwarded to target session, or unconfirmed

Operate in Executive KC mode: professional, friendly, polite, polished, helpful, and firm about closure. Every Slack task should end in one truthful state: sent, blocked, needs decision, needs verification, forwarded to target session, or timed out waiting for confirmation.

Telegram-facing completion updates for KC Slack actions should be minimal. Do not surface OpenClaw session ids, handoff mechanics, or detailed internal process recaps in Aya HQ unless Nathan asks. Prefer a terse result-only confirmation, for example: `Done - Jobber notes updated and Slack thread replied.`

## Decision rule

Choose the target surface before writing anything.

- **Top-level channel post**: use the real Slack write lane for the bound channel
- **Thread reply**: use the exact Slack thread session or Slack-native reply path
- **Telegram relay from Slack**: send to the target Telegram session directly
- **Slack relay from Telegram**: use the real Slack/message lane, not inter-session relay alone

Do not blur top-level channel work and thread work.
Read `/home/plife507/AYA-CLAW/references/topic-kc.md` when the request mixes Slack delivery with Jobber, costing, or PP workflow choices.

## Session targeting rules

### Top-level channel post

Primary rule:
- use the real Slack outbound lane, not `sessions_send` by itself

Helpful target references:
- channel session often looks like `agent:kc:slack:channel:<channelId>`
- `slack:#pp-dispatch-mgmt` / `C08CTUF1T7C`: PP job workflow and PP dispatch/margin posts
- `slack:#ops-frontstage` / `C07QEEN75EU`: connected KC channel and read source for HeyPros reviews / post-service audit data
- `slack:#dispatch-pm` / `C07U7Q01Q49`: PM dispatch channel target

The channel session can help with targeting context, but it is not itself proof of surface delivery.

### Thread reply

Use the exact thread session, typically shaped like:
- `agent:kc:slack:channel:<channelId>:thread:<threadTs>`

If the thread is referred to naturally, first use `kc-slack-thread-resolver` to bind the exact thread.

## Messaging rules

### For top-level channel posts

For top-level channel posts:

- do not treat `TOP>` as an active live trigger unless Nathan explicitly reinstates it
- prefer the **final user-visible post body**
- when Jobber ids are known, prefer a linked Job line using Slack mrkdwn links for the client and job number
- hard rule: build those links from verified Jobber record URLs, not guessed URL patterns; for jobs, prefer the exact Jobber work-order/job URL returned by Jobber for that record and fall back to plain text if the URL is not verified
- keep wrapper instructions minimal
- do not ask a Slack-bound session to "send to Slack" again
- do not recursively `sessions_send` to the same Slack session from inside that Slack session
- default to normal reply behavior for Slack-native mention handling unless a top-level post is explicitly requested
- use the CompanyCam revisit checklist only when Nathan explicitly says `revisit`; otherwise choose the normal checklist for the job type
- for recurring or revisit CompanyCam work, use the existing matching project/album; do not create a new CompanyCam project unless Nathan explicitly asks for a new album/project
- if an accidental empty duplicate CompanyCam project is created, use the CompanyCam CLI `projects merge --archive-empty-source` guard to archive it after the correct existing project has the checklist/users; non-empty duplicates must be merged in the CompanyCam web app
- for info-only revisit or coordination posts, omit `Sale`, `Sub Pay`, and `Margin`; keep the operational detail in `Notes:`
- when Nathan later adds an expense to an info-only PP post and explicitly says not to calculate P&L, edit or append the Slack note with the expense detail only; do not add sale, sub pay, or margin fields
- for recurring-job info posts, include margin inside the `Notes:` line when Nathan provides recurring economics like sub pay and sale price, but do not show sale price as its own field
- for recurring-job notes, calculate margin from the economics Nathan types in the note, as a per-visit calculator, rather than from Jobber quote totals unless he explicitly asks otherwise
- recurring-job info-only shape stays lean: `Job`, `Scope`, `Location`, `Notes`
- preferred recurring-note pattern: `Recurring <name> (Sub Pay: $X - Margin: $Z / NN.NN%)`
- house formatting matters:
  - single-sub P&L post: `Sub: <name>`
  - multi-sub P&L post: `Subs:` followed by one line per sub
- if Nathan asks for a KC day review based on "job messages we posted," use the actual Slack channel messages as the source set, not transcript recollection or only Aya-authored margin blocks

Clean execution order for Telegram KC requests that end in a Slack post:

1. identify that the target surface is a real top-level Slack channel post
2. resolve any Jobber data through the proper Jobber skill or wrapper first
3. build the exact final Slack body in KC house format
4. send through the real `message` Slack lane
5. report only confirmed delivery

Bad patterns:
- telling the Slack session to forward a message to Slack
- doing extra exploratory query churn after the job is already resolved well enough to execute
- mixing internal relay language with real Slack delivery language

Better pattern:
- give the Slack lane the exact final text that should appear as the post
- keep Jobber resolution, costing, and Slack delivery as three explicit steps
- stay in one canonical execution lane for the Slack task unless there is a real reason to switch

### For thread replies

- send the final reply text to the bound thread session
- do not use the top-level channel session when the request is clearly thread-bound
- preserve thread scope explicitly
- for an inbound Slack mention inside the target thread, the final assistant reply auto-posts there; do not also use `message(action="send")` to confirm in the same Slack thread
- if a user-visible Slack reply was already sent with the `message` tool, final output must be exactly `NO_REPLY` to prevent duplicate Slack responses

## Confirmation rules

Be exact about delivery state.

Allowed states:
- **sent**: the actual Slack surface clearly received the message
- **forwarded to target session**: the request was handed to another session, but surface delivery is not yet confirmed
- **timed out waiting for confirmation**: the handoff did not confirm in time
- **blocked/ambiguous**: target session, thread, or surface path was not clear enough
- **needs approval**: final body and target are ready, but posting requires Nathan's explicit approval

Never say a Slack post was sent if all you know is that an inter-session request timed out or echoed inside transcript history.

For confirmed successful Slack or Slack-plus-Jobber actions, report only the practical outcome in Telegram. Avoid "new session" announcements, exact session UUIDs, and verbose multi-action narration unless a blocker, ambiguity, or audit request requires it.

If blocked, report it as an investigation item: exact blocker, what is known, what is missing, risk of guessing, and the next verification step.

## Known failure modes

### 1. Thread carryover on a channel session

A channel session may still carry recent thread context.

Treat this as a real risk for top-level posting.
If the channel session behaves thread-sticky, do not pretend the target is clean.

### 2. Recursive self-send

A Slack-bound session can accidentally try to `sessions_send` to itself when given meta-instructions like "post this to Slack".

Avoid this by using the final post body or the real Slack/message lane directly.

### 3. Truth inflation

If a handoff to another session timed out, say that plainly.
Do not convert "forwarded" into "posted".

### 4. False success from `sessions_send`

`sessions_send` is inter-session relay only and runs with `deliver: false`.
Transcript output from that path is not Slack delivery confirmation.
Treat this as a hard rule, not a soft caution.

### 5. Double replies from same-thread message sends

In live Slack mention handling, the normal final assistant reply is already delivered back to the current channel or thread.

Avoid using `message(action="send")` for the same current Slack target unless the final output is exactly `NO_REPLY`.

## Practical operating model for KC

Use this split:

- `kc-slack-channel-operator` for top-level channel posts and cross-surface delivery behavior
- `kc-slack-thread-resolver` for exact thread discovery and thread binding
- `kc-pp-job-costing` for the actual nightly PP/sub-labor content
- `jobber-cli-v3-operator` for live Jobber lookup and write execution

That keeps:
- Jobber lookup and writes separate from
- content generation separate from
- Slack targeting separate from
- thread resolution

For a request like `job 20415 add expense for Vortex and post with margin to channel`, the clean skill chain is:

1. `jobber-job-identity` resolves the exact job if needed
2. `kc-slack-channel-operator` decides this is a real top-level Slack delivery task
3. `jobber-cli-v3-operator` performs the subcontractor expense write via the fixed wrapper
4. `kc-pp-job-costing` shapes the final P&L body
5. `kc-slack-channel-operator` sends it through the real Slack message path and reports confirmed delivery

## Read next when needed

- `references/channel-ops.md`
- `/home/plife507/AYA-CLAW/skills/kc-slack-thread-resolver/SKILL.md`
- `/home/plife507/AYA-CLAW/references/kc-slack-thread-ops-runbook.md`
- `/home/plife507/AYA-CLAW/skills/kc-pp-job-costing/references/pp-human-in-loop-workflow.md`
