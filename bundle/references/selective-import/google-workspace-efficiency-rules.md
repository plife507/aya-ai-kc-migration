# Google Workspace Efficiency Rules

Purpose: compact, current-state rules that make Aya faster and safer when working through Google Workspace.

## 1. Choose the correct Google lane first
- Use `gog` for Gmail, Sheets, Docs, Drive, Contacts, and Calendar user actions.
- Use `gcloud` for GCP admin, deploy, IAM, Cloud Run, Scheduler, Secret Manager, and service-account work.
- Do not blur the two just because both are Google.

## 2. Gmail, compose outside the command first
- Draft the final email as normal text before sending.
- Do not compose human-facing email directly inside shell-escaped syntax.
- Prefer a temp file, heredoc, or clean multiline body for anything longer than a couple sentences.
- For important replies, verify the sent message actually rendered correctly and threaded correctly.

## 3. Gmail, treat threading as untrusted until verified
- A matching subject line is not proof of correct threading.
- After an important reply, verify the thread id and where the message landed.
- "CLI accepted the command" is not the same as "Gmail threaded it correctly".

## 4. Sheets, never write blind
Before changing a sheet, inspect at least one of:
- spreadsheet metadata
- tab names
- target range values
- nearby rows/columns
- formulas, validation, or formatting when relevant

If the local pattern is not clear, stop reading and inspect more before writing.

## 5. Sheets, prefer the narrowest safe operation
Safe order:
1. read-only inspection
2. tight range update
3. append rows
4. tight formatting change
5. structural changes

Ask first before broad clears, delete-tab, rename-tab, global replace, or overwriting formula-heavy regions.

## 6. Sheets, preserve structure not just values
Assume live sheets may depend on:
- formulas
- dropdowns and validation rules
- hidden helper columns
- row order
- named ranges
- tab names referenced elsewhere

A write is not safe just because the cells look empty.

## 7. Sheets, prefer explicit shapes
- Prefer exact A1 ranges.
- Prefer `--values-json` over shorthand for important writes.
- Prefer reviewed row/column shape over fast delimiter syntax.

## 8. Verify after every mutation
After update, append, clear, or format:
- re-read the affected range
- confirm values landed correctly
- confirm nearby formulas/validation were not damaged when that matters

A success exit code is not enough.

## 9. Separate summary truth from detail mess
When designing or editing an operational sheet:
- keep summary tabs readable for humans
- move detail-heavy or relational mess into support tabs when needed
- preserve canonical IDs whenever possible
- do not flatten ambiguous source data into fake certainty

## 10. Surface ambiguity instead of hiding it
If source data is messy:
- mark review status
- preserve exception notes
- avoid silent auto-picks

The job is to expose reality cleanly, not fake clean data.

## 11. Report exact touch points after sheet work
When reporting back, include:
- spreadsheet or file reference if useful
- tab name
- exact range touched
- read-only vs changed
- what was verified after the action

## 12. Practical default
Inspect first. Write narrowly. Verify immediately. Use the right Google lane.
