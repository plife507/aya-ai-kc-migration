# Aya Workspace Dashboard

This repository is Aya's home workspace on Nathan's Linux host.

It holds operating memory, skills, references, runbooks, reports, scripts, and integration notes. Runtime secrets and private OpenClaw state live outside this repo unless explicitly documented otherwise.

## Start Here

- `TODO.md` - current operational dashboard and next actions
- `AGENTS.md` - workspace rules for agents
- `CLAUDE.md` - Claude worker posture and gated-workflow rules
- `MEMORY.md` - durable curated memory
- `memory/YYYY-MM-DD.md` - daily session notes

## Directory Map

- `references/` - stable runbooks and operating contracts
- `reports/` - dated audits, investigations, and implementation plans
- `phases/` - long-running gated phase plans
- `skills/` - canonical Aya skill store shared across agents
- `scripts/` - local operator scripts and wrappers
- `integrations/` - local integration experiments and services
- `kc/` - KC lane workspace view; skills are symlinked from the canonical `skills/` store

## Current Operating State

- OpenClaw is the primary operator runtime.
- Aya is the orchestrator; Claude, Codex, browser lanes, and CLIs are workers.
- KC work uses the KC lane and KC skills before broad tool use.
- TRADE work uses the TRADE topic/project lane and repo-rooted workers for `/home/plife507/Projects/TRADE`.
- External/public/destructive/credential-sensitive actions require explicit approval.

## Documentation Rule

When work changes operating behavior, sync it beyond chat:

- update the active control surface in `TODO.md` when the current plan changes
- update a relevant `references/` file for stable runbook behavior
- update a relevant `skills/*/SKILL.md` file when tool-routing behavior changes
- update `MEMORY.md` for durable preferences, decisions, or operating model changes
- append `memory/YYYY-MM-DD.md` for the session record

Do not create timestamped daily-note variants unless there is a specific exceptional reason.
