#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

require_bin() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "missing required command: $1" >&2
    exit 1
  fi
}

require_bin jq

jq -e '.name == "aya-ai-kc-ingestion"' ingestion-manifest.json >/dev/null
jq -e '(.include | length) > 0 and (.exclude | length) > 0' ingestion-manifest.json >/dev/null
jq -e 'all(.include[]; has("glob") and has("domain") and has("department") and has("priority"))' ingestion-manifest.json >/dev/null

if command -v rg >/dev/null 2>&1; then
  if rg -n --hidden --glob '!scripts/validate.sh' 'gho_|ghp_|xox[baprs]-|BEGIN (RSA|OPENSSH|PRIVATE)|refresh_token|access_token|AIza[0-9A-Za-z_-]{20,}' .; then
    echo "potential secret material matched; inspect output above" >&2
    exit 1
  fi
fi

echo "OK: ingestion plan and manifest validate."
echo "Include rules: $(jq '.include | length' ingestion-manifest.json)"
echo "Exclude rules: $(jq '.exclude | length' ingestion-manifest.json)"
