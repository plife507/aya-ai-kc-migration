# OpenClaw config baseline and checklist

## Live config file

Primary live config:

```bash
~/.openclaw/openclaw.json
```

Treat it as secret-bearing. Do not commit it raw.

## Current local posture

The following items were true during the latest config work:

- OpenClaw CLI/package currently reports `v2026.4.24`
- the systemd unit description/env may lag the CLI version; treat service metadata as stale until verified
- primary model is `openai/gpt-5.5` through the Codex embedded harness
- default thinking is `high`
- GPT-5 model runs get OpenAI `text_verbosity=low` by default unless model `params.text_verbosity` / `params.textVerbosity` override it
- workspace is `/home/plife507/AYA-CLAW`
- context engine slot uses `lossless-claw`
- enabled plugins include `openai`, `lossless-claw`, `telegram`, `memory-core`, `acpx`, and `browser`
- `secrets.providers.default` is an explicit env provider allowlisting the known OpenClaw secret variables
- browser plugin is enabled
- browser default profile is `openclaw`
- browser uses `/usr/bin/google-chrome-stable`
- browser config includes `headless: true` and `noSandbox: true`
- browser SSRF policy now explicitly allows `127.0.0.1` and `localhost`
- Telegram DM policy remains allowlist-based
- Telegram elevated access is scoped to the allowed Telegram sender only

Do not assume these remain true forever. Re-read before making sensitive changes.

## High-value edit targets

### Plugin enablement

Common checks:

```bash
python3 - <<'PY'
import json
cfg=json.load(open('/home/plife507/.openclaw/openclaw.json'))
print(cfg.get('plugins',{}))
PY
```

### Browser

Useful checks:

```bash
openclaw browser status
openclaw browser start
openclaw browser tabs
openclaw browser snapshot --format ai
```

The recent browser fix was config-only:

```json
"browser": {
  "ssrfPolicy": {
    "allowedHostnames": ["127.0.0.1", "localhost"]
  }
}
```

That change made native `openclaw browser start`, `status`, `tabs`, and `snapshot` work on this host.

### Telegram and elevated access

Keep these concepts separate:

- channel allowlist rules under `channels.telegram`
- elevated tool access under `tools.elevated.allowFrom`

Recent safe pattern:

- keep Telegram DM allowlist narrow
- keep group restrictions intact
- add only the intended Telegram sender for elevated access

## Restart checklist

After a config change that affects runtime behavior:

1. restart the gateway
2. verify the service is active
3. verify the exact feature you changed

Useful commands:

```bash
openclaw gateway restart
systemctl --user status openclaw-gateway.service --no-pager -l
openclaw status
```

Note: as of 2026-04-24, plain `openclaw status` fails in this config because the status command path tries to read Slack SecretRefs directly. Prefer `systemctl --user status openclaw-gateway.service --no-pager -l`, recent gateway logs, and `openclaw security audit` until the status lane is fixed or documented upstream.

## Verification checklist by change type

### Browser changes

- `openclaw browser status`
- `openclaw browser start`
- `openclaw browser tabs`
- `openclaw browser snapshot --format ai`

### Permission/elevated changes

- inspect the config block
- restart the gateway
- verify from the actual channel or target lane with a harmless test

### Model, thinking, and visibility changes

Keep these separate when diagnosing chat visibility:

- `/think` / `thinkingDefault` controls hidden model reasoning effort.
- `/reasoning on|stream` controls whether OpenClaw tries to surface reasoning summaries/streams.
- `/verbose on|full` controls OpenClaw tool-result/tool-output visibility. Use `on` for Nathan's normal Telegram mode so tool/process cards show without dumping full file reads or command output; reserve `full` for temporary debugging.
- GPT-5 `text_verbosity` controls answer verbosity only; it does not make tool calls appear as separate cards.
- GPT-5.5 via ACP also has `acp.stream`; for Nathan's preferred Telegram visibility, keep `acp.stream.deliveryMode=live` and expose non-private status/tool tags such as `tool_call`, `tool_call_update`, `plan`, `session_info_update`, and `agent_message_chunk`. Keep `agent_thought_chunk=false`; use action-level progress rather than raw chain-of-thought.

For GPT-5.5 visibility complaints, first check session status for `Text: low`, `verbose`, and `Reasoning`, then inspect `acp.stream`. Preferred steady state is `/verbose on` plus ACP live stream settings. Use `/verbose full`, `/reasoning stream`, or a model `params.text_verbosity` override only for targeted diagnostics.

- inspect the config block
- restart if needed
- confirm via `session_status` or observed runtime behavior

2026-04-26/27 local hotfix: ACP live mode alone was not enough to match Nathan's desired Telegram stream shape. The saved post-upgrade profile is: `agents.defaults.verboseDefault="on"`; existing non-slash Telegram sessions for `main` and `kc` use `verboseLevel="on"`; `channels.telegram.accounts.default.streaming.preview.toolProgress=false`; the Telegram bundle uses `suppressDefaultToolProgressMessages: previewToolProgressEnabled`; and the installed ACP dispatcher `resolveToolDetailText(event)` reads only `event.rawInput` so tool/process cards show without full file/output dumps. Reapply after OpenClaw upgrades with `/home/plife507/AYA-CLAW/scripts/reapply-openclaw-telegram-visibility-hotfix`, then verify with a tool-heavy Telegram turn.

## Secret-safe reporting rule

In summaries, include:

- changed keys
- purpose of the change
- restart required or not
- verification result

Do not include:

- raw bot tokens
- raw API keys
- OAuth client secrets
- full credential-bearing config dumps

## Git rule

If the user wants a commit for config work:

- commit a sanitized patch note or template
- do not commit the live `~/.openclaw/openclaw.json` unless the repo is explicitly private, intended for secrets, and the user clearly wants that
