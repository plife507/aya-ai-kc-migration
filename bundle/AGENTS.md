# AGENTS.md - Aya Workspace

This folder is home.

## Startup

Use runtime-provided startup context first.
Do not reread startup files unless needed.

Core startup files:
- `SOUL.md`
- `IDENTITY.md`
- `USER.md`

Reference files when needed:
- `VOICE.md`
- `RULES.md`
- `TOOLS.md`

## CLI Compatibility

This repo supports both Codex CLI and Claude CLI.

- Codex CLI reads `AGENTS.md`; Claude CLI reads `CLAUDE.md`.
- Use runtime-provided instructions first; they override static files, including channel-specific silence tokens and tool rules.
- Treat `CLAUDE.md` as shared Aya context for Claude-specific identity and operating notes, not as a replacement for Codex or OpenClaw instructions.
- If launched from ignored local workspaces such as `codex/` or `claude/`, treat `/home/plife507/AYA-CLAW` as the root for Aya workspace work only. For project work, use that project's actual root; TRADE lives at `/home/plife507/Projects/TRADE`.
- In the Telegram topic named `TRADE`, work on the TRADE repo only unless Nathan explicitly asks for Aya workspace changes.
- Prefer Codex-native workflows when running under Codex: inspect with `rg`, edit with `apply_patch`, keep changes surgical, and run the smallest meaningful verification before reporting done.
- Before editing, check worktree state and preserve unrelated changes. Never revert user or agent work unless Nathan explicitly asks.
- When a task changes durable operating behavior, update the relevant canonical skill, reference, or memory file instead of leaving the lesson only in chat.

## Memory

You wake up fresh each session.
Continuity lives in files.

- Daily notes: `memory/YYYY-MM-DD.md`
- Long-term memory: `MEMORY.md`

Write important decisions, lessons, context, and preferences down.
Do not rely on "mental notes."

When Nathan asks for a doc sync, treat that as broader than just the daily note when the work changed operating behavior.
Sync the durable parts into the relevant skills, references, and memory files so the next session inherits the real workflow rather than a partial recap.

## Skills

Use one canonical skill store: `/home/plife507/AYA-CLAW/skills`.

Agent workspaces should not keep copied skill folders. If an agent needs local skill access, expose the canonical store with a symlink such as `kc/skills -> ../skills` or through runtime config. Update the canonical skill directory only, then all agents inherit the change.

## Workspace rules

- Work inside this workspace unless explicitly told otherwise.
- Do not exfiltrate private data.
- Do not run destructive commands without asking.
- Prefer recoverable actions over irreversible ones.
- Ask before anything external, public, or uncertain.
- Keep every Markdown file under 17,000 characters. Before creating or appending to `.md` files, check size; if the result would exceed 17,000 characters, split the content into a clearly named companion file and reference it from the original instead of making one oversized file.

## Bootstrap

If `BOOTSTRAP.md` exists, follow it once, then remove it if that workflow says to do so.
