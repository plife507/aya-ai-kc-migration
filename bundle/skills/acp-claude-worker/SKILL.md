---
name: acp-claude-worker
description: Delegate repo coding work to Claude Code through OpenClaw ACP sessions. Use when the user wants Claude or Claude Code through ACP, when repo work should run as a one-shot or persistent ACP session, or when Aya should orchestrate serious phased development while Claude executes bounded coding work in a specific repo.
---

# ACP Claude Worker

Use this skill when Aya should use OpenClaw ACP to run Claude Code as a managed coding worker.

## Core operating model

- Aya is the orchestrator.
- ACP Claude is the repo coding worker.
- Prefer ACP when session continuity, steering, or persistent repo work matters.
- Use one-shot ACP for isolated tasks.
- Use persistent ACP sessions for iterative repo work across follow-ups.
- If ACP is unavailable, surface the blocker clearly and only use the local Claude headless fallback with approval.

## Required preflight

1. Confirm the target repo path.
2. Inspect the repo briefly first (`git status`, file layout, relevant files).
3. For serious development work, inspect whether the repo already has:
   - `TODO.md`
   - `phases/`
4. If the work is serious and those controls do not exist, recommend creating them before deep coding.

## TODO-and-gates workflow

For serious repo work:

- Treat `TODO.md` as the repo-level control surface.
- Treat `phases/` as the detailed phase execution and validation surface.
- Identify the active phase before delegating coding.
- Distinguish clearly between:
  - tasks = work to do
  - gates = proof thresholds
  - evidence = concrete proof that a gate passed
  - assumptions = relied-on but unproven conditions
  - blockers/open questions = reasons completion is unsafe or incomplete
- Do not mark a phase complete until its gates pass.
- If a gate fails, stop and surface it clearly.

## Delegation rules

When delegating serious repo work to ACP Claude:

1. Identify the current phase from `TODO.md` and the relevant phase doc.
2. Pass Claude the phase objective, scope, constraints, tasks, gates, and pass criteria.
3. Keep execution bounded to the active phase instead of letting Claude freewheel across the repo.
4. Require evidence back, not just a summary of edits.
5. Review whether gates actually passed before declaring success.

For smaller tasks, use a lighter prompt, but still require:

- clear objective
- scope limit
- minimal unrelated change
- relevant validation
- concise risk summary

## ACP session guidance

- Use `runtime: "acp"` with `agentId: "claude"`.
- Choose `mode: "run"` for one-shot work.
- Choose `mode: "session"` for persistent work.
- Keep the repo working directory explicit.
- When supported and appropriate, prefer Opus with effort set high and raise to max when needed.
- Prefer bounded prompts that say exactly what Claude should inspect, change, validate, and report back.

## Prompt guidance

For serious work, include:

- repo path
- active phase or instruction to identify it
- objective
- scope limit
- constraints and non-goals
- required gates
- required evidence
- validation to run
- summary format requested back

Example serious-work prompt:

```text
Inspect TODO.md and phases/ first. Identify the active phase and work only within that phase. Keep changes minimal and avoid unrelated refactors. Run the validation required by that phase. Report: files changed, gates passed or failed, evidence for each gate, assumptions, blockers/open questions, tests/validation run, and remaining risks. Do not claim phase completion unless the gates pass.
```

Example lighter prompt:

```text
Review the auth flow in this repo, keep the scope tight, make only the minimal required changes, run relevant validation, and report files changed, validation run, and remaining risks.
```

## Completion rule

Aya should not treat changed files as completion. Aya should review the returned evidence, verify whether the gates passed, and only then tell Nathan the phase or task is complete.
