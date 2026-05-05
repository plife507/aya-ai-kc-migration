---
name: kc-formatting
description: Use for KC Slack margin posts, recurring margin-style posts, job-info-only posts, and established KC output templates. Trigger when Nathan asks for a Slack post, margin post, recurring post, job-info post, or says to use the KC format/template. Also use when the exact linked Job line, Notes shape, or established blasting/work-order line-item format matters. For primary HeyPros offer drafting, use `heypros-job-offer`.
---

# KC Formatting

Use this skill to format KC outputs consistently before they are posted or pasted anywhere.

## Core rule

Do not improvise the shape when a known KC format exists.

When possible, verify Jobber-backed fields first, then format.
If the output is meant for Slack, show Nathan the draft here first unless he explicitly asks for immediate posting.
Keep KC-facing copy professional, friendly, polite, polished, helpful, and brief. Do not let private Aya/Nathan tone leak into Slack, customer, or subcontractor-facing text.
For KC day reviews requested from "job messages we posted," build from the actual Slack channel messages as the source set, not from memory, transcript echoes, or only Aya-authored margin blocks.
If the task mixes formatting with Jobber writes, Slack delivery, or PP sheet diagnosis, read `/home/plife507/AYA-CLAW/references/topic-kc.md` and keep formatting as its own step rather than absorbing the whole workflow.

## Output lanes

Choose one lane before writing.

### 1. Margin job post

Use this for one-off or standard P&L-style Slack posts.

Required shape:

- `Job: <client-url|Client Name> - <job-url|Job #12345>`
- `Scope:`
- `Location:`
- `Sale Price:`
- `Discount:`
- `Total:`
- `Sub Pay:`
- `Sub:` or `Subs:`
- `Notes:`
- `Margin:`

Rules:
- always hyperlink both the client name and the job number when Jobber URLs are available
- for client links, use the verified Jobber client path for that exact client record
- for job links, use the verified Jobber job/work-order URL returned by Jobber for that exact record (`jobberWebUri` or equivalent verified source); do not guess from visible job number and do not assume `/jobs/<jobNumber>` is correct
- if the exact Jobber URL is not verified yet, fall back to plain text instead of guessing a link
- include the `Location:` line
- use `Sub:` for a single subcontractor
- use `Subs:` with one line per sub for multi-sub jobs
- margin math should be based on quote-side economics when available
- if there is a quote-side discount, show it explicitly

Template:

```slack
Job: <client-url|Client Name> - <job-url|Job #12345>
Scope: ...
Location: ...
Sale Price: $X,XXX.XX
Discount: $X,XXX.XX
Total: $X,XXX.XX
Sub Pay: $X,XXX.XX
Sub: Name
Notes: ...
Margin: NN.NN% = $X,XXX.XX
```

### 2. Recurring margin-style post

Use the same linked/header structure as margin job posts.

Required shape:
- linked client
- linked job
- `Location:`
- same economics block
- default `Notes: Recurring` unless Nathan specifies other notes

Template:

```slack
Job: <client-url|Client Name> - <job-url|Job #12345>
Scope: ...
Location: ...
Sale Price: $X,XXX.XX
Discount: $X,XXX.XX
Total: $X,XXX.XX
Sub Pay: $X,XXX.XX
Sub: Name
Notes: Recurring
Margin: NN.NN% = $X,XXX.XX
```

### 3. Job-info-only post

Use when Nathan wants job identity/context without full P&L shape.

Required shape:
- `Job:`
- `Scope:`
- `Location:`
- `Notes:`

If recurring economics are provided inside the request, keep them inside `Notes:` unless Nathan asks for full margin shape.

Template:

```text
Job: ...
Scope: ...
Location: ...
Notes: ...
```

### 4. HeyPros blasting work order

Use this as the shape/template reference for HeyPros blasting work orders.
For primary HeyPros offer drafting, route first through `heypros-job-offer`, then use this template when needed.

Required shape:
- `Pay:`
- `Buyout Fee:`
- photo/link line when given
- `Prep Required:`
- `Required for Payment:`
- `Cleanup Required:`

Template:

```text
Pay: $X flat rate
Buyout Fee: $X
https://...

Prep Required:
- ...
- ...

Required for Payment:
- ...
- ...

Cleanup Required:
- ...
- ...
```

Blasting posture:
- include sqft when known
- include containment/protection expectations when known
- include success condition clearly
- include exclusions only when they materially matter
- keep it line-item, not narrative

## Verification checklist before finalizing

### For Slack margin posts

Verify when possible:
- exact job number
- client URL
- job URL
- confirm the job URL comes from a verified Jobber record path, not a guessed visible-number pattern
- location
- quote-side sale total and discount
- sub pay amount
- sub label/name
- notes text

### For HeyPros blasting work orders

Verify when possible:
- sqft
- prep requirements
- success condition / completion condition
- cleanup standard
- buyout fee
- photo link if Nathan provided one

## Call words Nathan can use

These phrases should route here directly:

### Slack / margin
- `margin post`
- `post margin`
- `kc margin format`
- `use margin format`
- `recurring margin post`
- `job info only`

### HeyPros / work order
- `blasting offer format`
- `use blasting format`
- `line item offer`

Primary HeyPros offer drafting should route to `heypros-job-offer`.

## Operating habit

If Nathan gives a short job stub like:
- client
- job number
- sub
- note

then:
1. resolve/verify Jobber fields
2. build the draft in the correct lane
3. show the draft here first
4. only then post or mutate if asked

If formatting cannot be completed because a required fact is missing, return the draft status as `needs verification` or `needs decision` and name the missing field plainly instead of inventing it.
