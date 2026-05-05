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
require_bin find

jq -e '.name == "aya-ai-kc-ingestion"' ingestion-manifest.json >/dev/null
jq -e '.name == "aya-ai-kc-migration-bundle"' migration-payload-manifest.json >/dev/null

required_paths=(
  "bundle/workspace/kc/AGENTS.md"
  "bundle/workspace/kc/docs/pp-job-workflow.md"
  "bundle/skills/kc-pp-job-costing/SKILL.md"
  "bundle/skills/jobber-cli-v3-operator/SKILL.md"
  "bundle/projects/jobber/jobber-cli-v3/package.json"
  "bundle/projects/kc-pp-sync/package.json"
  "bundle/projects/KC-SALES-SYNC/package.json"
  "bundle/config-templates/openclaw.redacted.json"
  "scripts/install-bundle.sh"
)

for path in "${required_paths[@]}"; do
  if [ ! -e "$path" ]; then
    echo "missing required payload path: $path" >&2
    exit 1
  fi
done

bad_files="$(find bundle \
  \( -name '.env' \
    -o -name '.env.local' \
    -o -name '*token*.json' \
    -o -name '*tokens*.json' \
    -o -name '*credentials*.json' \
    -o -name 'client_secret*.json' \
    -o -name '*.pyc' \
    -o -name '.git' \) \
  -print)"

if [ -n "$bad_files" ]; then
  echo "forbidden secret/runtime files found:" >&2
  echo "$bad_files" >&2
  exit 1
fi

bad_dirs="$(find bundle \
  \( -name 'node_modules' \
    -o -name '.git' \
    -o -name '.venv' \
    -o -name '__pycache__' \
    -o -name 'tokens' \
    -o -name 'keyring' \) \
  -type d -print)"

if [ -n "$bad_dirs" ]; then
  echo "forbidden secret/runtime directories found:" >&2
  echo "$bad_dirs" >&2
  exit 1
fi

if command -v rg >/dev/null 2>&1; then
  if rg -n --hidden \
    'gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{30,}|xox[baprs]-[A-Za-z0-9-]{20,}|sk-[A-Za-z0-9]{32,}|AIza[0-9A-Za-z_-]{25,}|-----BEGIN (RSA|OPENSSH|PRIVATE) KEY-----' \
    bundle scripts *.json *.md; then
    echo "potential live secret material matched; inspect output above" >&2
    exit 1
  fi
fi

if [ ! -x scripts/install-bundle.sh ]; then
  echo "scripts/install-bundle.sh is not executable" >&2
  exit 1
fi

echo "OK: migration bundle validates."
echo "Payload files: $(find bundle -type f | wc -l | tr -d ' ')"
echo "Skill files: $(find bundle/skills -type f | wc -l | tr -d ' ')"
echo "Project files: $(find bundle/projects -type f | wc -l | tr -d ' ')"
