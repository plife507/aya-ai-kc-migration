---
name: openclaw-browser-operator
description: Run browser work under Aya through OpenClaw using a hybrid two-lane model. Use when Nathan wants browser automation, browser research, tab control, screenshots, structured extraction, login-aware browsing, or live browser coaching under OpenClaw rather than Claude Code. Routes simple or isolated work toward the managed browser lane and escalates login-heavy, MFA, session-bound, or user-visible work toward the live attached browser lane.
---

# OpenClaw Browser Operator

Use this skill when browser work should happen under Aya in OpenClaw.

## Core model

Aya uses two browser lanes:

1. **Managed lane** (`profile: "openclaw"`)
   - isolated browser
   - best for simple, repetitive, low-risk work
   - good for tab automation, screenshots, extraction, scheduled checks, and non-login flows

2. **Live attached lane** (`profile: "user"`)
   - attaches to Nathan's real local Chrome session through Chrome DevTools MCP
   - best for authenticated flows, MFA, dashboards, weird sites, and live coaching

Default philosophy:

- simple first
- isolated when practical
- escalate to live attached only when the task needs real session state or visible collaboration
- do not route browser work through Claude unless Nathan explicitly wants Claude involved

## Decision rule

Choose the lane before acting.

### Use the managed lane when

- the site does not need Nathan's logged-in session
- the task is mostly navigation, reading, screenshots, or structured extraction
- the task can run in an isolated profile
- you want lower risk and cleaner state

### Use the live attached lane when

- the site needs existing cookies, logins, or MFA
- Nathan wants visible browser collaboration
- the site behaves differently in a real signed-in session
- the managed lane is blocked or unreliable on the current host

### Stop and surface the blocker when

- neither lane is healthy
- the task would require broader desktop control rather than browser automation
- the site appears to require risky workarounds, stealth tooling, or policy-sensitive behavior

## Workflow

### 1. Classify the task

Put the task in one of these buckets:

- **simple browser task**: open tabs, inspect pages, extract info, capture screenshots
- **account/session task**: login state, dashboards, authenticated actions
- **live coaching task**: Nathan should see or guide the flow in real time
- **blocked browser task**: browser route unhealthy, anti-bot wall, or browser is the wrong tool

### 2. Pick the lane

- simple browser task -> start with `openclaw`
- account/session task -> use `user`
- live coaching task -> use `user`
- blocked browser task -> surface the blocker and recommend the next best path

### 3. Preflight checks

For any lane:

- confirm browser plugin/config is enabled if there is reason to doubt it
- check `openclaw browser status`
- use an explicit browser profile when the lane matters

For `user` lane:

- Nathan should have Chrome running locally
- remote debugging must be enabled in Chrome inspect settings
- Nathan may need to approve the first attach prompt

For `openclaw` lane:

- verify the managed profile can start cleanly before promising unattended automation
- if the managed lane fails on this host, do not hide it, switch to `user` only with Nathan's awareness

### 4. Execute with the right posture

Managed lane posture:

- prefer it for low-risk automation
- keep actions deterministic
- prefer snapshots, screenshots, and structured reads over brittle assumptions

Live attached posture:

- treat it as sensitive because it uses Nathan's real session
- prefer minimal required actions
- warn when the site might trigger consent, MFA, or account-side side effects

### 5. Escalation ladder

Escalate in this order:

1. managed `openclaw`
2. live attached `user`
3. node-host or remote-CDP architecture if the browser must live elsewhere
4. desktop-control or another tool only if browser automation is genuinely insufficient and Nathan approves

Do not jump straight to Browser Use or Claude Code unless there is a real gap.

## Current local posture

Read `/home/plife507/AYA-CLAW/skills/openclaw-browser-operator/references/hybrid-browser-workflow.md` when you need the current host-specific findings, local commands, or rollout notes.

## Command patterns

### Managed lane

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw tabs
openclaw browser --browser-profile openclaw snapshot
```

### Live attached lane

```bash
openclaw browser --browser-profile user start
openclaw browser --browser-profile user status
openclaw browser --browser-profile user tabs
openclaw browser --browser-profile user snapshot --format ai
```

## Output rules

When replying about browser work:

- say which lane you chose
- say why that lane fits
- separate observed facts from assumptions
- surface blockers plainly instead of papering over them
- if escalation is needed, name the next lane and why
