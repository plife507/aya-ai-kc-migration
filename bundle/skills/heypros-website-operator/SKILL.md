---
name: heypros-website-operator
description: Operate the KC HeyPros website through OpenClaw browser automation, especially login-aware navigation, public reachability checks, screenshots, extraction, and Preferred Partner / PP review entry. Use when Nathan asks Aya to work inside heypros.com, kc-power-clean.heypros.com, HeyPros dashboard pages, HeyPros reviews, Prefered Parner/Preferred Partner reviews, PP reviews, or specific browser click sequences for KC HeyPros workflows.
---

# HeyPros Website Operator

Use this skill for KC HeyPros website operation.

This is the browser-operation lane for HeyPros. It is separate from `heypros-job-offer`, which drafts subcontractor-facing offer text.

## Core posture

HeyPros is production business software. Work read-first, keep actions narrow, and do not submit writes unless Nathan explicitly approves the exact write action.

Before acting:
- identify whether the task is read-only, login/session work, or a production write
- choose the browser lane using `openclaw-browser-operator`
- surface browser health blockers plainly
- use screenshots/snapshots/evaluate output to ground what you saw

## Known KC entry point

- KC workspace sign-in: `https://kc-power-clean.heypros.com/sign-in`
- Login email: `opsscheduling@kcpowerclean.com`

Do not submit login, OTP, review forms, or production changes without explicit go-ahead for that step.

## Browser lane guidance

Use `openclaw` managed lane when:
- the task is public/non-authenticated
- checking reachability or page shape
- capturing screenshots or extracting visible text from a non-sensitive page

Use `user` live attached lane when:
- the task requires Nathan's signed-in session
- MFA/OTP is involved
- Nathan wants to watch or guide the interaction
- the managed lane is unreliable on the current host

Current local note: OpenClaw 2026.4.24 exposes browser commands through the OpenClaw browser plugin/CLI. `click-coords` is available for viewport-coordinate clicks:

```bash
openclaw browser click-coords 120 340
```

The installed build exposes coordinate clicking, not a separate pure `move-mouse x y` command.

## Current browser findings

As of 2026-04-26:
- `https://kc-power-clean.heypros.com/sign-in` loads and shows `Sign In | HeyPros`
- sign-in initially shows phone login, with `Use Email Instead`
- `openclaw` and `user` browser profiles are configured as Chrome MCP existing-session attach lanes
- `openclaw` expects Chrome attach on port `9223`
- `user` expects Chrome attach on port `9222`
- managed attach has been flaky when `DevToolsActivePort` is stale
- `evaluate`, `tabs`, and `doctor` worked after correcting the live DevTools browser websocket path
- `snapshot` hit a temp-file ENOENT once under `/tmp/openclaw/openclaw-chrome-mcp-*`
- `console` is unsupported in the current gateway build because Playwright is unavailable

## Preferred Partner review entry

Preferred Partner review entry is a production write workflow. Treat it as fragile and sequence-sensitive.

When Nathan asks for PP review entry:
1. Read `references/preferred-partner-review-entry.md`.
2. Confirm source review data and target job/customer before opening a write form.
3. Navigate and inspect first; do not submit.
4. If the sequence depends on coordinates, capture viewport size and screenshot path before clicking.
5. Use `click-coords` only when refs are missing, unstable, or misleading.
6. Stop before final submit unless Nathan explicitly says to submit this specific review.
7. After submission, verify the saved state by reading the page back.

## Command patterns

Prefer explicit browser profile flags:

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw tabs
openclaw browser --browser-profile openclaw snapshot
openclaw browser --browser-profile openclaw screenshot
openclaw browser --browser-profile openclaw click-coords 120 340
```

For the live attached lane:

```bash
openclaw browser --browser-profile user status
openclaw browser --browser-profile user tabs
openclaw browser --browser-profile user snapshot
openclaw browser --browser-profile user screenshot
```

## Output rules

When reporting HeyPros browser work:
- say which browser lane was used
- separate observed facts from assumptions
- mention whether any production write was avoided, staged, or submitted
- include the final verification method when a write is approved and completed
- if blocked, name the exact browser/profile/tool failure and the next best path

## References

Read when needed:
- `/home/plife507/AYA-CLAW/skills/heypros-website-operator/references/preferred-partner-review-entry.md`
- `/home/plife507/AYA-CLAW/skills/openclaw-browser-operator/SKILL.md`
- `/home/plife507/AYA-CLAW/skills/heypros-job-offer/SKILL.md`
- `/home/plife507/AYA-CLAW/skills/kc-pp-sync-operator/references/business-cautions.md`
