# OpenClaw Telegram Visibility Hotpatch Investigation

Date: 2026-05-03
Host: `/home/plife507/AYA-CLAW`
Observed OpenClaw version: `2026.4.24 (cbcfdf6)`

## Purpose

Nathan's preferred Telegram behavior is the April 21 style: compact live tool/process cards in Telegram, normal assistant text, no hidden reasoning, and no giant dumps of file contents or command output.

The hotpatch is not one setting. It spans:

- live config: `~/.openclaw/openclaw.json`
- session stores: `~/.openclaw/agents/*/sessions/sessions.json`
- compiled OpenClaw JS bundles under the global npm install
- local reapply helpers in this workspace

This is why copying only one visible setting to a new machine does not reproduce the behavior.

## Desired Behavior

- Show compact live tool/process updates before the final answer.
- Keep `verboseLevel` at `on`, not `full`.
- Keep `agent_thought_chunk` hidden.
- Show normal assistant messages.
- Show concise command/read/memory/plan cards.
- Do not serialize whole events, stdout/stderr, full file reads, secrets, raw JSON, stack traces, auth headers, cookies, or hidden reasoning.

## Live Config

Primary config:

```text
/home/plife507/.openclaw/openclaw.json
```

Secret-safe values observed:

```text
agents.defaults.verboseDefault = "on"
agents.defaults.thinkingDefault = "high"
channels.telegram.accounts.default.streaming.preview.toolProgress = false
acp.stream.deliveryMode = "live"
acp.stream.coalesceIdleMs = 350
acp.stream.maxChunkChars = 1200
acp.stream.maxSessionUpdateChars = 1200
acp.stream.tagVisibility.tool_call = true
acp.stream.tagVisibility.tool_call_update = true
acp.stream.tagVisibility.usage_update = true
acp.stream.tagVisibility.available_commands_update = true
acp.stream.tagVisibility.current_mode_update = true
acp.stream.tagVisibility.config_option_update = true
acp.stream.tagVisibility.session_info_update = true
acp.stream.tagVisibility.plan = true
acp.stream.tagVisibility.agent_message_chunk = true
acp.stream.tagVisibility.agent_thought_chunk = false
```

Unset in the current live config, although the older helper knows about them:

```text
agents.defaults.silentReply.direct = <unset>
agents.defaults.silentReplyRewrite.direct = <unset>
channels.telegram.streaming.preview.toolProgress = <unset>
acp.stream.repeatSuppression = <unset>
```

`repeatSuppression` currently falls back to the compiled dispatcher default, which is `true`.

## Session Stores

Session files found:

```text
/home/plife507/.openclaw/agents/main/sessions/sessions.json
/home/plife507/.openclaw/agents/kc/sessions/sessions.json
/home/plife507/.openclaw/agents/codex/sessions/sessions.json
/home/plife507/.openclaw/agents/claude/sessions/sessions.json
```

Observed Telegram session state:

```text
main: 5 Telegram sessions, 1 slash session, 2 verboseLevel="on", 3 unset
kc:   4 Telegram sessions, 1 slash session, 2 verboseLevel="on", 2 unset
codex: 0 Telegram sessions
claude: 0 Telegram sessions
```

The helper is intended to set existing non-slash Telegram sessions to `verboseLevel="on"`. On a new machine there may be no existing sessions, so `agents.defaults.verboseDefault="on"` is the durable default that matters first.

## Runtime Files

Global OpenClaw root observed:

```text
/home/plife507/.nvm/versions/node/v24.14.1/lib/node_modules/openclaw
```

Bundle names change after upgrades. Locate files by anchors, not by exact filenames.

### ACP Dispatcher

Current file:

```text
/home/plife507/.nvm/versions/node/v24.14.1/lib/node_modules/openclaw/dist/dispatch-acp-CEqX6KWn.js
```

Patched behavior observed:

```text
function resolveToolDetailText(event) {
  const candidates = [event.rawInput];
}

function renderToolSummaryText(event) {
  const args = normalizeToolArgsForDisplay(toolName, event.rawInput);
}

allowEdit: Boolean(toolCallId && event.tag === "tool_call_update")
```

Meaning:

- tool detail comes from `event.rawInput` only
- compact cards are rendered through `resolveToolDisplay()` and `formatToolSummary()`
- previous `rawInput` is preserved across lifecycle updates
- `tool_call_update` messages can edit a prior card

Without this, ACP tool events can stay invisible, lose useful args, or include too much raw detail.

### Telegram Bot Bundle

Current file with relevant dispatch code:

```text
/home/plife507/.nvm/versions/node/v24.14.1/lib/node_modules/openclaw/dist/extensions/telegram/bot-gUR32RLX.js
```

Observed behavior:

```text
previewToolProgressEnabled =
  Boolean(answerLane.stream) && resolveChannelStreamingPreviewToolProgress(telegramCfg)

suppressDefaultToolProgressMessages: previewToolProgressEnabled
```

Because config sets:

```text
channels.telegram.accounts.default.streaming.preview.toolProgress = false
```

`previewToolProgressEnabled` becomes false for the default Telegram account, so the default ACP/tool progress messages are not suppressed by Telegram's generic preview lane. This is the interaction that replaces the generic `Working...` behavior with compact ACP tool cards.

### Tool Display Bundle

Current file:

```text
/home/plife507/.nvm/versions/node/v24.14.1/lib/node_modules/openclaw/dist/tool-display-DahNA8kW.js
```

Observed patched mappings:

```text
update_plan -> title "Plan"
memory_get  -> title "Memory Get"
```

This is mostly cosmetic, but it is part of the visible Telegram profile.

### ACPX Runtime Bridge

Current ACPX extension files:

```text
dist/extensions/acpx/register.runtime.js
dist/extensions/acpx/register.runtime-b8kSOZpz.js
dist/extensions/acpx/runtime-api.js
```

The current reapply helper tries to resolve `acpx/runtime` as a package export. That did not resolve on this install. This is a real replication hazard: the helper can fail before applying the patch.

## Helper Scripts

Two helper scripts exist:

```text
scripts/reapply-openclaw-telegram-visibility-hotfix
scripts/reapply-openclaw-telegram-visibility-hotfix 2
```

### Current Helper

`scripts/reapply-openclaw-telegram-visibility-hotfix` currently:

- finds the global OpenClaw root
- sets `agents.defaults.verboseDefault="on"`
- sets `channels.telegram.accounts.default.streaming.preview.toolProgress=false`
- sets existing non-slash Telegram sessions to `verboseLevel="on"`
- patches the ACP dispatcher
- tries to patch an ACPX runtime bridge
- patches Telegram suppression behavior
- patches tool-display labels
- validates JS syntax with `node --check`
- restarts `openclaw-gateway.service` unless `--no-restart` is passed

Current issue: it looks for `acpx/runtime`, but this install exposes ACPX files under `dist/extensions/acpx/*.js` instead.

### Older Helper With Space-Suffix

`scripts/reapply-openclaw-telegram-visibility-hotfix 2` is a different generation of the patch. It:

- assumes defaults like `/home/aya/.openclaw/openclaw.json`
- sets global and account Telegram preview `toolProgress=false`
- sets `agents.defaults.silentReply.direct="allow"`
- sets `agents.defaults.silentReplyRewrite.direct=false`
- sets ACP stream config including `repeatSuppression=true`
- patches standalone Telegram tool progress functions
- calls `scripts/patch-openclaw-acp-stream.py`

Current issue: `scripts/patch-openclaw-acp-stream.py` does not exist in this workspace. This helper cannot be used as-is.

## Backups

Config backups exist:

```text
/home/plife507/.openclaw/openclaw.json.bak-20260426-telegram-tool-progress
/home/plife507/.openclaw/openclaw.json.bak-20260427-000446-telegram-visibility
/home/plife507/.openclaw/openclaw.json.bak-20260427-000515-telegram-visibility
/home/plife507/.openclaw/openclaw.json.bak-20260427-000620-telegram-visibility
/home/plife507/.openclaw/openclaw.json.bak-20260427-205618-telegram-visibility
/home/plife507/.openclaw/openclaw.json.bak-20260501-112620-telegram-visibility
/home/plife507/.openclaw/openclaw.json.bak-20260501-223132-telegram-visibility
```

Runtime bundle backups include timestamped copies of:

```text
dist/dispatch-acp-CEqX6KWn.js
dist/extensions/telegram/bot-gUR32RLX.js
dist/tool-display-DahNA8kW.js
```

Do not blindly restore old bundles onto a new OpenClaw version. Use backups only as references for patch intent.

## New Machine Reproduction Checklist

1. Verify OpenClaw and find the install.

```bash
openclaw --version
OPENCLAW_ROOT="$(npm root -g)/openclaw"
test -d "$OPENCLAW_ROOT/dist"
```

2. Apply config keys without dumping secrets.

Required durable keys:

```json
{
  "agents": { "defaults": { "verboseDefault": "on", "thinkingDefault": "high" } },
  "channels": { "telegram": { "accounts": { "default": { "streaming": { "preview": { "toolProgress": false } } } } } },
  "acp": {
    "stream": {
      "deliveryMode": "live",
      "coalesceIdleMs": 350,
      "maxChunkChars": 1200,
      "maxSessionUpdateChars": 1200,
      "tagVisibility": {
        "tool_call": true,
        "tool_call_update": true,
        "usage_update": true,
        "available_commands_update": true,
        "current_mode_update": true,
        "config_option_update": true,
        "session_info_update": true,
        "plan": true,
        "agent_message_chunk": true,
        "agent_thought_chunk": false
      }
    }
  }
}
```

Optional keys from the older helper, useful if direct-message `NO_REPLY` rewrites or global Telegram preview settings become a problem:

```json
{
  "agents": { "defaults": { "silentReply": { "direct": "allow" }, "silentReplyRewrite": { "direct": false } } },
  "channels": { "telegram": { "streaming": { "preview": { "toolProgress": false } } } },
  "acp": { "stream": { "repeatSuppression": true } }
}
```

3. Patch existing session stores after backing them up.

For `~/.openclaw/agents/*/sessions/sessions.json`, set non-slash Telegram sessions to:

```json
{ "verboseLevel": "on" }
```

4. Locate current runtime bundles by anchors.

```bash
DISPATCHER="$(rg -l 'function resolveToolDetailText\(event\)' "$OPENCLAW_ROOT/dist"/dispatch-acp-*.js | head -1)"
TELEGRAM_BOT="$(rg -l 'suppressDefaultToolProgressMessages' "$OPENCLAW_ROOT/dist/extensions/telegram"/*.js | head -1)"
TOOL_DISPLAY="$(rg -l 'memory_get: \{' "$OPENCLAW_ROOT/dist"/tool-display-*.js | head -1)"
```

5. Patch goals for the runtime bundles.

- Dispatcher: `resolveToolDetailText(event)` reads only `event.rawInput`.
- Dispatcher: `renderToolSummaryText(event)` uses `event.rawInput` and `tool-display`.
- Dispatcher: `emitToolSummary()` preserves prior `rawInput` and allows editing `tool_call_update`.
- Telegram bot: default tool progress suppression depends on `previewToolProgressEnabled`, not hardcoded true.
- Tool display: keep known plan and memory-get labels.

6. Validate syntax before restart.

```bash
node --check "$DISPATCHER"
node --check "$TELEGRAM_BOT"
node --check "$TOOL_DISPLAY"
```

7. Restart and verify.

```bash
openclaw gateway restart || systemctl --user restart openclaw-gateway.service
systemctl --user is-active openclaw-gateway.service
```

Then send a Telegram turn that triggers several tools. Expected result: compact live cards appear, final assistant text appears, no hidden reasoning or full file dump appears.

## Why Replication Is Failing

Most likely causes:

1. Only config was copied; compiled JS bundles also need patching.
2. The wrong helper was used; the space-suffix helper depends on a missing Python patcher.
3. The current helper is version-fragile because `acpx/runtime` does not resolve here.
4. Bundle filenames changed after upgrade; hardcoded filenames are not portable.
5. Existing Telegram sessions kept older or unset `verboseLevel`.
6. Telegram preview progress was not disabled at the account level, so generic `Working...` preview behavior can suppress desired cards.

## Recommended Cleanup

Consolidate the two helper scripts into one version-aware helper before using this on a new machine:

- archive or remove `scripts/reapply-openclaw-telegram-visibility-hotfix 2`
- replace the unresolved `acpx/runtime` lookup with anchors under `dist/extensions/acpx`
- include all intended config keys in one place
- fail with a clear diagnostic if an anchor is not found
- print exact files patched
- always create backups before editing
- run `node --check` on every modified JS file
- support `--no-restart` and `--restart-if-changed` consistently

Until then, use this investigation doc as the source of truth and treat both helper scripts as partial references.
