# Hybrid browser workflow for Aya under OpenClaw

## Purpose

Aya should handle browser work through OpenClaw, not through Claude Code by default.

The operating model is a two-lane browser system:

- **managed headless/isolated lane** for simple, repeatable, lower-risk work
- **live attached lane** for authenticated, session-bound, or coached work

## Lane map

### Lane 1: managed browser (`openclaw` profile)

Use for:

- opening and organizing tabs
- page reading and structured extraction
- screenshots and simple visual checks
- routine site checks
- low-risk form fills
- scheduled or repeated browser tasks

Strengths:

- isolated from Nathan's personal session
- cleaner state
- better default lane for unattended work
- better for repeatability

Current local note:

- browser plugin is enabled in `~/.openclaw/openclaw.json`
- `browser` is in `plugins.allow`
- current config pins Chrome at `/usr/bin/google-chrome-stable`
- current config sets `headless: true` and `noSandbox: true`
- managed profile startup is still unhealthy on this host: OpenClaw logs show Chrome starts, but the CDP websocket is not reachable after start

Implication:

- keep this as the intended simple-task lane
- do not assume it is production-ready on this machine until the startup issue is resolved

### Lane 2: live attached browser (`user` profile)

Use for:

- logins and MFA
- signed-in dashboards
- session-dependent websites
- difficult sites that behave differently in a real browser session
- live coaching or visible collaborative browsing

Strengths:

- uses Nathan's actual browser state
- aligned with OpenClaw docs for local Chrome MCP workflows
- strongest near-term path on this host

Requirements:

- local Chrome running on the same host
- Chrome version 144+
- remote debugging enabled from `chrome://inspect/#remote-debugging`
- Nathan available to approve initial attach consent if prompted

Current local note:

- Chrome 147 is present locally
- OpenClaw docs favor this route for existing signed-in session use
- this is the recommended near-term operational lane on the current machine

## Recommended routing rule

1. Start with `openclaw` for simple isolated work.
2. If the task needs login state, MFA, visible collaboration, or the managed lane is unhealthy, use `user`.
3. If local browser placement is wrong, move to node-host or remote CDP.
4. Only after a real gap appears should Browser Use or desktop control be considered.

## OpenClaw-specific commands

### General inspection

```bash
openclaw browser status
openclaw browser profiles
openclaw doctor
```

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

## Workflow notes

### For simple work

- prefer the managed lane first
- if it fails, say that clearly
- then recommend the live attached lane instead of pretending the isolated lane is healthy

### For complicated work

- prefer the live attached lane first
- keep actions minimal because this lane touches real browser state
- expect attach consent and site-side friction

### For rollout

Recommended order on this host:

1. make the `user` lane healthy and routine
2. validate real tasks through it
3. return to repairing the managed `openclaw` lane
4. once both lanes are stable, make the routing automatic by task type

## Things to avoid

- do not treat Claude's browser tooling as Aya's primary browser path
- do not install random browser stacks without a concrete reason
- do not hide managed-lane health problems behind vague language
- do not use workarounds without surfacing the blocker and getting Nathan's approval first
