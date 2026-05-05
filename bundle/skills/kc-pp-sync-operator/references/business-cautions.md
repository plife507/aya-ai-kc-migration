# KC PP Sync — Business Cautions

## Matching and data-shape cautions

Important current behavior from repo docs and verification work:
- archived HeyPros jobs are not currently returned by the `jobsDashboard` API path that was tested
- completed or closed work can be returned as `Done`
- duplicate PO or job-number returns in HeyPros often reflect real recurring or multi-work-order patterns, not necessarily bugs

Do not label duplicates a defect before checking the business shape.

## HeyPros posture

Treat HeyPros as effectively read-only unless Nathan explicitly approves writes.

Use read-first verification for:
- auth state
- returned job shape
- PO matching behavior
- duplicate patterns

## Sheet vs sync logic rule

When something looks wrong in the sheet, ask:
1. is this a one-off manual data issue?
2. is this expected output from the sync logic?
3. is this a runtime failure or partial-sync symptom?

Do not patch over a generated issue with a manual sheet edit without noting that the root cause may live in code or runtime.

## Margin cautions

Margin behavior is conditional:
- margin is computed only after payment conditions are met
- unpaid, uninvoiced, or hybrid states can leave margin blank
- recurring tabs do not have margin column C

Do not assume a missing margin is automatically a bug.

## Output interpretation cautions

Keep these distinctions clear:
- month tabs are operational outputs
- recurring tabs are structurally different outputs
- GTP tabs are reporting/output surfaces
- Dashboard is a summary surface
- Command / Log is sync evidence

When a user asks for a fix, decide whether they want:
- a sheet correction
- an explanation of generated output
- a runtime diagnosis
- a code-level follow-up
