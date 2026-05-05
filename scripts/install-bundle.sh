#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_OPENCLAW="${TARGET_OPENCLAW:-$HOME/.openclaw}"
TARGET_PROJECTS="${TARGET_PROJECTS:-$HOME/Projects}"
DRY_RUN=0

usage() {
  cat <<'USAGE'
Usage: ./scripts/install-bundle.sh [options]

Options:
  --target PATH       OpenClaw target root. Default: $HOME/.openclaw
  --projects PATH     Projects target root. Default: $HOME/Projects
  --dry-run           Show what would be copied without writing files
  -h, --help          Show this help

Environment:
  TARGET_OPENCLAW     Same as --target
  TARGET_PROJECTS     Same as --projects
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      TARGET_OPENCLAW="$2"
      shift 2
      ;;
    --projects)
      TARGET_PROJECTS="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if ! command -v rsync >/dev/null 2>&1; then
  echo "missing required command: rsync" >&2
  exit 1
fi

copy_dir() {
  local src="$1"
  local dst="$2"
  if [ ! -d "$src" ]; then
    echo "skip missing source: $src"
    return
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] rsync $src/ -> $dst/"
    rsync -ani "$src/" "$dst/" | sed -n '1,120p'
  else
    mkdir -p "$dst"
    rsync -a "$src/" "$dst/"
    echo "copied $src -> $dst"
  fi
}

echo "OpenClaw target: $TARGET_OPENCLAW"
echo "Projects target: $TARGET_PROJECTS"

copy_dir "$ROOT/bundle/skills" "$TARGET_OPENCLAW/skills"
copy_dir "$ROOT/bundle/workspace/kc" "$TARGET_OPENCLAW/workspaces/agents/kc"
copy_dir "$ROOT/bundle/config-templates" "$TARGET_OPENCLAW/config-templates"

if [ "$DRY_RUN" -eq 0 ]; then
  mkdir -p "$TARGET_PROJECTS"
fi
for project_dir in "$ROOT"/bundle/projects/*; do
  [ -d "$project_dir" ] || continue
  copy_dir "$project_dir" "$TARGET_PROJECTS/$(basename "$project_dir")"
done

cat <<EOF

Install copy complete.

Next steps:
1. Rehydrate secrets and env files on the target host.
2. Wire OpenClaw config from bundle/config-templates/openclaw.redacted.json.
3. Install project dependencies where needed.
4. Run service-specific tests/builds before deploy.
EOF
