---
name: claude-headless-worker
description: Run Claude Code headlessly as Aya's local coding worker on this Linux machine. Use when coding work should be delegated to Claude in a specific repo, especially medium or large repo tasks, phased development, TODO.md plus phases/ workflows, repo review, bug fixing, refactors, or when checking whether the local Claude headless wrapper is available.
---

# Claude Headless Worker

Use this skill when Aya should orchestrate repo work and local Claude Code should execute the coding pass.

## Use this skill for

- medium or large coding tasks in a real repo
- repo inspection, bug fixing, refactors, and test writing
- serious development work that should follow `TODO.md` plus `phases/`
- cases where the user explicitly wants Claude Code as the coding engine

## Do not use this skill for

- simple one-line edits Aya can do directly
- tasks inside `~/AYA-CLAW` unless the user explicitly wants Claude working there
- vague requests without a target repo path

## Core operating model

- Aya is the orchestrator.
- Claude is the repo coding worker.
- Aya scopes the task, bounds the work, reviews the result, and decides whether gates actually passed.
- Do not treat code changes as completion.

## Required preflight

1. Work in a specific repo, preferably under `~/Projects/...`.
2. Inspect the repo briefly first (`git status`, file layout, relevant files).
3. For serious development work, inspect whether the repo already has:
   - `TODO.md`
   - `phases/`
4. If the work is serious and those controls do not exist, recommend creating them before deep coding.

## TODO-and-gates workflow

For serious development work:

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

When delegating serious repo work to Claude:

1. Identify the current phase from `TODO.md` and the relevant phase doc.
2. Pass Claude the phase objective, scope, constraints, tasks, gates, and pass criteria.
3. Keep execution bounded to the active phase instead of letting Claude freewheel across the repo.
4. Require evidence back, not just a summary of edits.
5. Review whether gates actually passed before declaring success.

For smaller tasks, a lighter prompt is acceptable, but still require:

- clear objective
- scope limit
- minimal unrelated change
- relevant validation
- concise risk summary

## Invocation options

Use the local wrapper:

- `~/.local/bin/claude` for direct CLI access
- `~/.local/bin/claude-headless <repo> <prompt>` for headless repo-scoped execution

Check availability:

```bash
~/.local/bin/claude --version
```

Run headless in a repo:

```bash
~/.local/bin/claude-headless /home/plife507/Projects/my-repo "Work only on the active phase in TODO.md and phases/. Keep changes bounded to that phase, run the required validation, and report gates, evidence, blockers, and files changed."
```

Direct invocation:

```bash
cd /home/plife507/Projects/my-repo && ~/.local/bin/claude --permission-mode bypassPermissions --print "Inspect TODO.md and phases/, identify the active phase, work only within that scope, run relevant validation, and report gates, evidence, blockers, and risks."
```

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
Fix the login error path in the API client. Keep the patch minimal, avoid unrelated refactors, run relevant tests if available, and summarize files changed, tests run, and remaining risks.
```

## Notes

- The local `claude` wrapper resolves the installed Claude binary from known local paths.
- The headless wrapper keeps execution repo-scoped and avoids mixing Aya state with project code.
- Prefer Opus and high effort for Claude headless runs when available.
- If Claude is unavailable, verify the local install path first.
