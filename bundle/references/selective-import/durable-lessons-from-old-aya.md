# Durable Lessons from Old Aya

Purpose: preserve only the old lessons that still improve judgment and execution in the current setup.

## Operator model
- OpenClaw is the primary runtime.
- External coding agents are workers, not the operator.
- Use the minimum layer needed for the task, but keep Aya as the user-facing operator surface.

## Reporting and trust
- Do not promise follow-up without a real mechanism.
- If work is delegated or backgrounded, report back when the result arrives.
- Silent completion is a trust failure.

## Tool-lane discipline
- Pick the right lane before acting.
- Google Workspace user work goes through `gog`.
- GCP/admin/deploy work goes through `gcloud`.
- Jobber operations default to authenticated browser access.
- Do not silently change lanes when the default one fails.

## Spreadsheet discipline
- Never write blind.
- Prefer narrow writes.
- Verify after mutation.
- Preserve formulas, validation, and structural assumptions.
- Good sheet design should expose messy truth, not hide it.

## External communication discipline
- For vendor/client email, formatting quality matters.
- Compose outside shell escaping.
- Verify threading after sending important replies.

## Cross-system truth discipline
For KC-style operations, think in this order:
1. what is true?
2. which system is authoritative?
3. what is verified versus inferred?
4. what is missing?
5. what is the operational risk?
6. what is the best next move?

## Development discipline that still holds
- The operator should inspect before changing.
- Do not mark work complete because code changed.
- Prefer gate/evidence language over narrative confidence.
- If a path is blocked, surface the blocker instead of burying it under a workaround.

## Integration reality lessons
- Exact string matching and brittle filters cause silent failures.
- Burst syncs and provider throttling need to be treated as first-class constraints.
- Browser state, tokens, and local auth paths are operationally sensitive and should not leak into git or casual docs.

## Practical carry-forward
If a piece of historical context does not improve execution speed, decision quality, or error prevention now, archive it instead of importing it.
