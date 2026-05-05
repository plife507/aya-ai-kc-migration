#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./scripts/apply-telegram-visibility-profile.sh [options]

Applies the durable Telegram visibility settings used by the current KC Aya host.
It updates OpenClaw JSON config and existing Telegram session records. Runtime
bundle hotpatches are version-sensitive, so this script verifies their anchors
and points to the bundled investigation doc if they need manual reapplication.

Options:
  --config PATH      OpenClaw config path. Default: $HOME/.openclaw/openclaw.json
  --no-restart      Do not restart openclaw-gateway.service
  --check-runtime   Check installed OpenClaw runtime bundle anchors
  -h, --help        Show this help
USAGE
}

CONFIG="${HOME}/.openclaw/openclaw.json"
RESTART_GATEWAY=1
CHECK_RUNTIME=0
STAMP="$(date +%Y%m%d-%H%M%S)"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --config)
      CONFIG="$2"
      shift 2
      ;;
    --no-restart)
      RESTART_GATEWAY=0
      shift
      ;;
    --check-runtime)
      CHECK_RUNTIME=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

require_bin() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "missing required command: $1" >&2
    exit 1
  fi
}

backup_file() {
  local file="$1"
  [ -f "$file" ] || return 0
  cp "$file" "$file.bak-$STAMP-telegram-visibility"
}

patch_config() {
  require_bin node
  if [ ! -f "$CONFIG" ]; then
    echo "missing OpenClaw config: $CONFIG" >&2
    exit 1
  fi

  backup_file "$CONFIG"
  node - "$CONFIG" <<'NODE'
const fs = require("fs");
const file = process.argv[2];
const data = JSON.parse(fs.readFileSync(file, "utf8"));

data.agents ??= {};
data.agents.defaults ??= {};
data.agents.defaults.verboseDefault = "on";
data.agents.defaults.thinkingDefault = "high";

data.channels ??= {};
data.channels.telegram ??= {};
data.channels.telegram.accounts ??= {};
data.channels.telegram.accounts.default ??= {};
const account = data.channels.telegram.accounts.default;
account.streaming ??= {};
account.streaming.preview ??= {};
account.streaming.preview.toolProgress = false;

data.acp ??= {};
data.acp.stream ??= {};
data.acp.stream.deliveryMode = "live";
data.acp.stream.coalesceIdleMs = 350;
data.acp.stream.maxChunkChars = 1200;
data.acp.stream.maxSessionUpdateChars = 1200;
data.acp.stream.tagVisibility = {
  tool_call: true,
  tool_call_update: true,
  usage_update: true,
  available_commands_update: true,
  current_mode_update: true,
  config_option_update: true,
  session_info_update: true,
  plan: true,
  agent_message_chunk: true,
  agent_thought_chunk: false
};

fs.writeFileSync(file, JSON.stringify(data, null, 2) + "\n");
NODE
  echo "updated config: $CONFIG"
}

patch_sessions() {
  require_bin node
  local sessions_root="${HOME}/.openclaw/agents"
  [ -d "$sessions_root" ] || return 0

  while IFS= read -r sessions_file; do
    [ -f "$sessions_file" ] || continue
    backup_file "$sessions_file"
    node - "$sessions_file" <<'NODE'
const fs = require("fs");
const file = process.argv[2];
const data = JSON.parse(fs.readFileSync(file, "utf8"));
const sessions = data.sessions && typeof data.sessions === "object" ? data.sessions : data;
let changed = 0;
for (const [key, session] of Object.entries(sessions)) {
  if (!key.includes(":telegram:")) continue;
  if (key.includes(":slash:")) continue;
  if (!session || typeof session !== "object") continue;
  if (session.verboseLevel !== "on") {
    session.verboseLevel = "on";
    changed += 1;
  }
}
fs.writeFileSync(file, JSON.stringify(data, null, 2) + "\n");
console.log(`${file}: telegram sessions verboseLevel=on (${changed} changed)`);
NODE
  done < <(find "$sessions_root" -path '*/sessions.json' -print 2>/dev/null | sort)
}

check_runtime() {
  require_bin npm
  require_bin rg

  local npm_root root dist dispatcher telegram_bot tool_display
  npm_root="$(npm root -g 2>/dev/null || true)"
  root="${OPENCLAW_ROOT:-${npm_root}/openclaw}"
  dist="$root/dist"
  if [ ! -d "$dist" ]; then
    echo "runtime check skipped: could not find OpenClaw dist at $dist" >&2
    return 1
  fi

  dispatcher="$(rg -l 'function resolveToolDetailText\(event\)' "$dist"/dispatch-acp-*.js 2>/dev/null | head -n 1 || true)"
  telegram_bot="$(rg -l 'suppressDefaultToolProgressMessages' "$dist"/extensions/telegram/*.js 2>/dev/null | head -n 1 || true)"
  tool_display="$(rg -l 'memory_get: \{' "$dist"/tool-display-*.js 2>/dev/null | head -n 1 || true)"

  echo "OpenClaw root: $root"
  echo "dispatcher anchor: ${dispatcher:-missing}"
  echo "telegram bot anchor: ${telegram_bot:-missing}"
  echo "tool display anchor: ${tool_display:-missing}"

  if [ -z "$dispatcher" ] || [ -z "$telegram_bot" ] || [ -z "$tool_display" ]; then
    echo "runtime anchors are incomplete; see bundle/docs/openclaw-telegram-visibility-hotpatch-investigation-2026-05-03.md" >&2
    return 1
  fi
}

restart_gateway() {
  [ "$RESTART_GATEWAY" -eq 1 ] || {
    echo "skipped gateway restart (--no-restart)"
    return 0
  }

  if command -v openclaw >/dev/null 2>&1 && openclaw gateway restart >/dev/null 2>&1; then
    echo "gateway restarted with openclaw gateway restart"
    return 0
  fi

  if command -v systemctl >/dev/null 2>&1; then
    systemctl --user restart openclaw-gateway.service
    systemctl --user is-active --quiet openclaw-gateway.service
    echo "gateway restarted and active"
    return 0
  fi

  echo "could not restart gateway automatically; restart OpenClaw manually" >&2
}

patch_config
patch_sessions
if [ "$CHECK_RUNTIME" -eq 1 ]; then
  check_runtime
fi
restart_gateway

cat <<'DONE'

Telegram visibility profile applied:
- verboseDefault=on
- Telegram account preview.toolProgress=false
- ACP live stream tags match the current host
- existing Telegram sessions use verboseLevel=on

For exact post-upgrade runtime hotpatch behavior, keep the bundled investigation
doc with this script and verify with a tool-heavy Telegram message after restart.
DONE
