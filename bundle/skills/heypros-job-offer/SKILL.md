---
name: heypros-job-offer
description: Prepare, review, and format KC HeyPros job offers across multiple subcontractor-facing formats, including blasting offers, line-item work orders, and other recurring HeyPros offer shapes. Use when Nathan asks for a HeyPros offer, work order, subcontractor-facing post, crew-facing job text, offer cleanup, or wants a job drafted into the correct HeyPros format without drifting into unrelated Jobber, Slack, or PP workflow steps.
---

# HeyPros Job Offer

Use this skill for KC HeyPros offer and work-order drafting.

This is the primary lane for subcontractor-facing HeyPros offer text.
It is not the broad Jobber lane, not the Slack delivery lane, and not the PP costing lane.

## Core rule

Keep HeyPros offer work explicit and format-aware.

- verify the source details first when possible
- identify which HeyPros offer type Nathan wants
- shape the offer text in the correct house format for that job type
- keep the output subcontractor-facing, professional, friendly, polite, polished, practical, and easy to act on
- be helpful but firm about completion requirements, payment requirements, prep, cleanup, and missing details
- do not blur this into Jobber writes, Slack posting, or PP sync diagnosis

If the request mixes HeyPros offer work with other KC steps, read `/home/plife507/AYA-CLAW/references/topic-kc.md` and keep the lanes separate.

## When to use this skill

Use this skill when Nathan asks for things like:
- `make a HeyPros offer`
- `write the work order`
- `clean up this subcontractor offer`
- `turn this scope into a HeyPros post`
- `draft the offer text for the crew`
- `use the blasting format`
- `use the HeyPros format`
- `make this into the right offer type`

Use `kc-formatting` alongside this skill when you need the exact established shape/template for a known format.

## Source posture

For HeyPros-related work:
- treat HeyPros as the subcontractor/work-order truth where relevant
- use read-first verification when checking job shape or work-order context
- treat HeyPros as effectively read-only unless Nathan explicitly approves writes
- do not label duplicate work orders or duplicate PO/job-number returns as defects before checking whether the business shape is recurring or multi-work-order

## Workflow

1. Identify the offer type
Pick the correct offer shape before drafting.

Common examples:
- blasting / surface-prep offer
- structured line-item work order
- general subcontractor-facing offer
- cleanup or rewrite of existing HeyPros text
- other recurring HeyPros house formats as they are established

2. Verify the available facts
- pay
- buyout fee if any
- location
- sqft, quantity, or scope size if relevant
- prep requirements
- completion/payment requirements
- cleanup expectations
- exclusions if they materially matter
- photo or link if provided

3. Choose the output shape
- use the exact house format when one already exists
- use line-item structure when the job is crew-facing and operational
- keep the text concise and practical
- avoid narrative fluff and avoid burying actionable requirements

4. Draft the text
- make the scope clear
- make the success condition clear
- make payment requirements clear
- separate prep, payment, and cleanup when the format calls for it
- keep the language easy for a subcontractor to scan quickly

5. Show Nathan the draft first unless he explicitly asks for immediate posting or entry

## Format routing rule

Do not assume all HeyPros offers use one shape.

Route by job type and existing house format:
- if the job is blasting-style and operationally detailed, use the blasting/work-order line-item format
- if Nathan refers to a known recurring HeyPros format, use that exact format
- if the format is unclear but the job details are present, draft in the closest established subcontractor-facing shape and say which shape you used
- if multiple plausible formats exist, ask Nathan which one he wants instead of guessing

## Standard blasting/work-order shape

Use this when the job is blasting-style and the line-item operational shape fits:

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

## Content rules

- include sqft when known
- include containment/protection expectations when known
- include the completion standard clearly
- include exclusions only when they materially matter
- keep the text line-item when the job type calls for it
- do not invent job facts that were not provided or verified

## Boundaries

- do not turn a HeyPros offer request into a Jobber write by default
- do not turn a formatting request into a Slack delivery step by default
- do not fold PP costing into the offer unless Nathan explicitly wants economics included
- if key details are missing, ask for the missing pieces instead of bluffing
- if a format is not yet established, say so instead of pretending there is already a locked template

## Good answer shape

If enough detail is present:
- return the cleaned draft in the chosen HeyPros format
- if useful, label the format briefly

If details are missing:
- ask briefly for the exact missing items, for example pay, buyout fee, sqft, cleanup standard, or which HeyPros format Nathan wants
- label the state as `needs decision` or `needs verification` rather than drafting around missing facts

## References

Read these when needed:
- `/home/plife507/AYA-CLAW/skills/kc-formatting/SKILL.md`
- `/home/plife507/AYA-CLAW/references/topic-kc.md`
- `/home/plife507/AYA-CLAW/skills/kc-pp-sync-operator/references/business-cautions.md`
