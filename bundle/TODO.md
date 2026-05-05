# Aya Dashboard

## Purpose

This is the active control surface for the Aya home workspace.

Use this file to answer three questions quickly:
- what is active
- what is safe to use now
- what needs the next verification pass

Detailed phase notes live in `reports/` and `phases/`. Stable operating rules live in `references/`, `skills/`, `MEMORY.md`, and `memory/YYYY-MM-DD.md`.

## Current Snapshot

- **Date:** 2026-04-25
- **Active initiative:** system-wide config cleanup and operating-boundary hardening
- **Execution mode:** gated, evidence-driven
- **Current focus:** memory/doc-sync boundaries, then broader tool/elevated/browser/backup cleanup

## Usable Lanes

- **HQ / main:** Telegram DM, Aya HQ topic `1`, TRADE topic `5` for now, LIFE topic `7` for now
- **KC:** Aya HQ topic `3`, Slack `#pp-dispatch-mgmt` (`C08CTUF1T7C`)
- **TRADE:** usable as a project lane, but not yet split into a dedicated OpenClaw agent
- **LIFE:** usable as a topic lane, but not yet split into a dedicated OpenClaw agent

KC routing and Slack thread finalization have passed live proof. Continue normal approval guardrails for external messages, Jobber writes, invoices, expenses, credential changes, and other irreversible actions.

## Active Work

Primary plan:
- `reports/system-wide-config-cleanup-todo-2026-04-24.md`

Focused completed/near-completed sub-plans:
- `reports/kc-agent-isolation-todo-and-test-plan-2026-04-24.md`
- `reports/kc-executive-assistant-gsd-todo-2026-04-24.md`

Supporting long-running architecture plan:
- `phases/phase-0-aya-resilience-plan.md`

## Next Actions

- [ ] Define memory/doc-sync boundaries clearly enough that future sessions know what belongs in daily notes, `MEMORY.md`, references, skills, and reports.
- [ ] Finish the `.openclaw` permission/category inventory and document target modes by file class.
- [ ] Resolve or document the `openclaw status` SecretRef/runtime boundary.
- [ ] Review tool/elevated/web/browser boundaries after the docs pass.
- [ ] Run a final harmless verification sweep across Telegram, Slack, memory, browser, and gateway after cleanup items land.

## Phase Board

- [x] Phase 0 - inventory and classification started
- [ ] Phase 1 - reversible permission and secret-hygiene fixes
- [ ] Phase 2 - OpenClaw runtime config baseline and verification
- [x] Phase 3 - Telegram topic routing first pass
- [x] Phase 4 - KC Slack workflow routing first pass
- [ ] Phase 5 - tool/elevated/web/browser boundary review
- [ ] Phase 6 - memory and doc-sync boundary review
- [ ] Phase 7 - backup, restore, and healthcheck verification

## Known Issues

- `openclaw status` from shell can fail on unresolved Slack SecretRefs outside the active gateway runtime snapshot.
- `openclaw security audit` is currently the safer audit lane for secret-safe findings.
- Some generated runtime/session sidecar files have previously appeared at `664`; service `UMask=0077` is in place, but new-file behavior still needs follow-up verification.
- Old mixed `main`/`kc` sessions may remain on disk as legacy state. Fresh route resolution is the source of truth.

## Doc Map

- `README.md` - workspace map and operating dashboard
- `TODO.md` - active control surface
- `references/README.md` - durable reference index
- `reports/README.md` - audit and plan index
- `phases/README.md` - phase-plan index
- `skills/*/SKILL.md` - executable workflow instructions
- `MEMORY.md` - durable curated memory
- `memory/YYYY-MM-DD.md` - daily session record

## Gate Rule

Before creating or restructuring a serious project TODO, check `CLAUDE.md` and use the gated TODO/phases structure unless the task is too small to justify it.

A phase is not done because files changed. A phase is done only when its success barriers are met and verified.
