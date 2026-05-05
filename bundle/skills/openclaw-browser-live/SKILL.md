---
name: openclaw-browser-live
description: Use Aya's live attached OpenClaw browser lane for authenticated, session-bound, or coached browser work. Trigger when a task needs Nathan's real Chrome session, existing cookies, MFA, visible collaboration, or a more realistic live browser surface than the isolated managed lane.
---

# OpenClaw Browser Live

Use this skill for the live attached OpenClaw browser lane.

## When to use it

Choose this skill when:

- the task needs Nathan's signed-in browser state
- MFA, dashboards, or account context matter
- Nathan wants to watch, guide, or collaborate live
- the isolated managed lane is blocked or unreliable

## Operating posture

- Use `profile: "user"`.
- Treat this lane as sensitive because it touches Nathan's real browser session.
- Keep actions minimal and intentional.
- Expect attach consent or browser-side prompts.

## Required local conditions

- Chrome running locally
- remote debugging enabled in `chrome://inspect/#remote-debugging`
- Nathan available to approve the first attach if prompted

## Core commands

```bash
openclaw browser --browser-profile user start
openclaw browser --browser-profile user status
openclaw browser --browser-profile user tabs
openclaw browser --browser-profile user snapshot --format ai
```

## Escalate away when

- the browser needs to live on another machine, in which case use node-host or remote CDP
- the task is not really browser automation and needs broader desktop control
- the requested action becomes high-risk or unclear

For broader routing and current host notes, read `/home/plife507/AYA-CLAW/references/openclaw-browser-workflow.md`.
