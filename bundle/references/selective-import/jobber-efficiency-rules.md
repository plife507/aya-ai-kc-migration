# Jobber Efficiency Rules

Purpose: preserve only the Jobber patterns that make future Aya work cheaper, faster, and less error-prone.

## 1. Default Jobber access mode correctly
For real Jobber work, default to authenticated browser access, not public-site research and not API mode unless explicitly requested.

Working interpretation:
- actual Jobber operations → authenticated browser lane
- public docs/marketing lookup → web research
- tokens/endpoints/integrations → API lane

Do not silently switch lanes if one fails.

## 2. Browser-authenticated Jobber access is sensitive
Assume browser state may contain:
- cookies
- local/session storage
- browsing history
- downloaded artifacts

Treat browser profile state as local-only and non-git material.

## 3. Never let ambiguous Jobber requests stay ambiguous
If a request does not clearly identify the target job or target action, fail out loud instead of guessing.

Examples that require clarification:
- no job number
- multiple plausible jobs
- unclear whether the action is Jobber, Slack-only, or another system

## 4. Notes should be summarized, not dumped
Default internal Jobber note style:
- concise
- operational
- normalized from messy chat context
- verbatim only if explicitly requested

Good default shape:
- source/context label if helpful
- short bullets for multi-part updates
- preserve names, dates, promises, and requested actions

## 5. Read the minimum context needed
When converting a message or thread into a Jobber action:
- read the triggering message
- read only the minimum surrounding context needed to resolve the job and intent
- stop once target job and action are unambiguous

Do not ingest a whole thread if the answer is already clear.

## 6. Snapshot-heavy browser work is the token burner
When browser automation is involved:
- prefer deterministic DOM/evaluate flows over repeated snapshots
- use snapshots only when refs or visual confirmation are actually needed
- once on the correct page, use the cheapest reliable submit/verify path

## 7. Visible Jobber number is not always the real internal locator
Do not assume the visible Jobber job number maps directly to the internal URL path or object locator.
Use the cheapest reliable on-site lookup path instead of guessing URLs.

## 8. Failure policy
If the documented/default Jobber lane fails:
- fail out loud
- do not silently downgrade to public-site mode
- do not silently switch to API mode
- ask before changing the access strategy

## 9. Cross-system use case to remember
For KC work, Jobber is the primary execution hub.
That means future Jobber work often matters because it connects to:
- HeyPros work orders
- subcontractor/payment tracking
- internal note workflows
- Google Sheets reporting surfaces

## 10. Practical default
Resolve the right job fast, read only the context needed, use the correct access lane, write concise internal notes, and avoid expensive browser wandering.
