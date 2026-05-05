---
name: openclaw-browser-managed
description: Use Aya's managed OpenClaw browser lane for simple, isolated, low-risk browser work. Trigger when the task is tab automation, page reading, screenshots, structured extraction, or routine browsing that does not need Nathan's real signed-in browser session.
---

# OpenClaw Browser Managed

Use this skill for the isolated OpenClaw browser lane.

## When to use it

Choose this skill when:

- the site does not need Nathan's login state
- the task is simple or repetitive
- screenshots, extraction, tab control, or low-risk automation are the goal
- isolation is better than using the real browser session

## Operating posture

- Use `profile: "openclaw"`.
- Prefer deterministic actions and small steps.
- Treat this as the default simple-task lane.
- If the managed lane is unhealthy on the current host, say so plainly and escalate to the live attached lane rather than hiding the failure.

## Core commands

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw tabs
openclaw browser --browser-profile openclaw snapshot
```

## Escalate away when

- login, MFA, or existing cookies matter
- Nathan wants live visible collaboration
- the managed browser fails to start or attach cleanly

For broader routing and current host notes, read `/home/plife507/AYA-CLAW/references/openclaw-browser-workflow.md`.
