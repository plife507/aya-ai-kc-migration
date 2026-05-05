# Coding Worker Router Bakeoff Notes

## Purpose

Capture the concrete local observations that justify the routing rule.

## Observed outcomes

### Focus Timer patch bakeoff
Two parallel repos implemented the same bounded feature set on a small plain HTML/CSS/JS timer app.

Task shape:
- dark/light theme toggle with persistence
- draining progress bar
- preset buttons
- minimal patching only
- no framework or large restructure

Outcome:
- Codex was the stronger default for this bounded patch task.
- It inspected first, patched in place, and self-corrected an edge-case mismatch in progress direction.
- Claude also completed successfully, but Codex felt more operationally crisp for this scope.

Routing lesson:
- prefer Codex for bounded implementation and patch-in-place work

### Friction Log greenfield bakeoff
Two fresh repos built the same tiny SPA from scratch with localStorage, helpers, tests, README, and required git commit.

Outcome:
- Claude completed the end-to-end repo workflow including commit.
- Codex produced the app structure and validation but did not complete the required commit because `.git/index.lock` was blocked in its sandboxed lane.

Routing lesson:
- prefer Claude when repo closure and commit completion are part of done

### Buggy Habit Streak repair bakeoff
Two repos started from the same intentionally broken app.

Task shape:
- diagnose duplicate-day bug
- fix stale current-streak logic
- surface saved habit name in UI
- improve raw history rendering
- add tests proving the bugfixes
- make a git commit when done

Outcome:
- Both lanes diagnosed the real bug shape correctly.
- Codex was fast and clean in shared-logic-first repair work.
- Claude completed the repair plus commit cleanly.
- Codex again hit repo-finalization friction on commit.

Routing lesson:
- Codex is excellent for diagnosis and bounded code repair
- Claude is safer when full repo completion is required

## Durable conclusion

Best current local rule:
- Codex = fastest builder and patcher
- Claude headless = safer finisher and repo closer
- Aya = scoper, reviewer, verifier

## Use this reference when

Read this file when you need the empirical basis for the routing choice, or when deciding whether a new coding task looks more like a fast patch lane or a full closure lane.
