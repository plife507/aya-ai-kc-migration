---
name: coding-worker-router
description: Route local coding work between Codex and Claude headless based on task shape, finish requirements, and verification needs. Use when Aya must choose the best worker lane for repo coding, bugfixes, refactors, scratch experiments, or bounded implementation on this Linux host, especially after deciding whether speed or full end-to-end repo completion matters more.
---

# Coding Worker Router

Choose the worker deliberately. Aya stays the orchestrator.

## Core rule

Pick the lane that best matches the real finish condition, not the brand name.

- Use Codex when speed, patch quality, and bounded implementation matter most.
- Use Claude headless when the job must reliably reach full repo closure, especially when commit completion is part of done.
- Keep Aya responsible for scoping, verification, and final judgment.

## Default routing

### Choose Codex for
- small to medium bounded implementation
- patch-in-place UI or logic work
- quick bugfixes with clear scope
- scratch builds and experiments
- tasks where fast diagnosis is valuable
- cases where Nathan may want rapid iteration over polish theater

Observed strengths on this host:
- fast inspection and diagnosis
- clean in-place patches
- good momentum on bounded tasks
- strong performance in side-by-side patch bakeoffs

Known weakness on this host:
- may fail at final git commit in sandboxed or constrained repo situations even when the code and tests are done

### Choose Claude headless for
- tasks where commit completion is part of the required finish
- end-to-end repo workflows that need stronger closure
- heavier reasoning or slightly more careful finalization
- larger bugfix chains where follow-through matters as much as speed
- tasks where a cleaner repo-finishing lane is worth a little extra latency

Observed strengths on this host:
- strong end-to-end completion
- better reliability when the brief includes tests plus commit
- solid discipline on bounded repo work

## Practical decision rule

Ask one question first:

What actually counts as done?

- If done means implement or repair the code cleanly and fast, prefer Codex.
- If done means finish the repo workflow all the way through tests and commit, prefer Claude.

## Recommended operating pattern

1. Inspect the repo or scratch app first.
2. Define the task boundary tightly.
3. State the finish condition clearly.
4. Pick the worker lane.
5. Require a short end report with:
   - root cause or implementation summary
   - files changed
   - tests run
   - commit hash if required
   - explicit validation notes
6. Review the result before declaring success.

## Bounded delegation rules

- Do not hand the worker an open-ended architecture rewrite unless that is truly the task.
- Prefer minimal clean patches over unnecessary restructuring.
- Require tests or verification appropriate to the scope.
- If commit is required, say so explicitly in the worker brief.
- Treat summaries as untrusted until Aya verifies the outcome.

## Current durable policy on this machine

- Aya is the orchestrator.
- Codex is the default fast builder and patcher.
- Claude headless is the safer finisher when end-to-end repo closure matters.
- For serious project work, continue to use TODO.md plus phases/ gates when present.

## Suggested brief shape

Include:
- what is broken or needed
- what constraints matter
- what not to change
- what verification is required
- whether commit is required

Example finish line:
- inspect first
- make the smallest clean fix
- run the relevant checks
- report files changed and validation
- make a git commit when done

## When to override the default

Override toward Claude when:
- the repo task is sensitive
- the user explicitly wants stronger closure
- prior Codex runs hit repo-finalization friction

Override toward Codex when:
- the task is highly iterative
- speed of implementation matters most
- the repo-finalization step is optional or can be handled separately

## References

Read `references/bakeoff-notes.md` if you want the concrete observed patterns behind this routing rule.
