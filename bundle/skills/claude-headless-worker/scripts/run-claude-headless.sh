#!/usr/bin/env bash
set -euo pipefail

repo="${1:-}"
shift || true
prompt="$*"

if [ -z "$repo" ] || [ -z "$prompt" ]; then
  printf 'usage: run-claude-headless.sh <repo-path> <prompt>\n' >&2
  exit 64
fi

exec /home/plife507/.local/bin/claude-headless "$repo" "$prompt"
