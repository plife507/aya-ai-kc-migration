---
name: openclaw-config-operator
description: Safely inspect and update the live OpenClaw config on this machine, especially `~/.openclaw/openclaw.json`, plugin enablement, browser config, Telegram/elevated access rules, model-thinking defaults, and Gateway restarts. Use when Aya needs to patch OpenClaw behavior without breaking the pinned install or leaking secrets.
---

# OpenClaw Config Operator

Use this skill when changing live OpenClaw behavior on this host.

## Core rule

Treat `~/.openclaw/openclaw.json` as a live secret-bearing production config.

That means:

- inspect before editing
- make the smallest targeted change
- preserve current working posture unless the user asked otherwise
- restart only when needed and verify after
- never commit or paste the raw config into git or chat

## Safe workflow

### 1. Read the live state first

Check the relevant part of the config before changing anything.

Common targets:

- `plugins.allow`
- `plugins.entries.*`
- `browser.*`
- `channels.telegram.*`
- `tools.elevated.*`
- `agents.defaults.*`
- `session.*`

### 2. Decide whether this is low-risk

Low-risk examples:

- enabling a plugin already installed
- adding an allowlisted sender/channel entry
- adjusting browser settings
- changing model or thinking defaults

Pause and surface risk when the change would:

- widen exposure broadly
- change auth posture in a hard-to-reverse way
- remove protections
- alter runtime behavior beyond the requested scope

### 3. Edit minimally

Prefer targeted edits over full rewrites.

When patching:

- keep unrelated keys untouched
- preserve the current version pin and install path assumptions
- do not delete allowlists, group restrictions, or security settings unless explicitly requested
- redact secrets in any summary or patch note

### 4. Restart deterministically when needed

Preferred restart:

```bash
openclaw gateway restart
```

If a direct CLI restart is not the right lane, use the existing user service path.

### 5. Verify the change

Use the smallest verification that proves the target behavior.

Examples:

```bash
openclaw status
openclaw browser status
openclaw browser start
systemctl --user status openclaw-gateway.service --no-pager -l
```

For permission changes, verify the exact target surface rather than assuming the restart worked.

## Common tasks

### Telegram and elevated access

When enabling Telegram elevated access:

- keep `channels.telegram.allowFrom` narrow
- keep group mention rules intact unless asked otherwise
- add only the intended Telegram sender under `tools.elevated.allowFrom.telegram`

### Browser config

For browser work:

- confirm `browser` is in `plugins.allow`
- confirm `plugins.entries.browser.enabled = true`
- verify `browser` settings separately from general plugin enablement
- verify with real browser commands, not just config inspection

### Model and thinking defaults

For main-agent defaults:

- inspect `agents.defaults.model.primary`
- inspect `agents.defaults.thinkingDefault`
- inspect `session` keys only if session-level behavior is relevant

## Local reference

Read `references/config-baseline-and-checklist.md` for:

- current local posture
- restart and verification checklist
- secret-safe reporting rules
- examples from recent Telegram and browser config work

## Output style

Keep replies precise:

- say what changed
- say what stayed intentionally unchanged
- call out restart requirements
- call out risks or tradeoffs
- never include raw tokens or secret values
