---
name: x-cost-aware-operator
description: Reduce X API/XMCP cost while still getting useful answers. Use when working with X posts, users, timelines, trends, news, or docs through XMCP/X docs, especially for discovery, research, watchlists, account inspection, and repeated follow-up queries where broad search can waste credits.
---

# X Cost Aware Operator

Use X as an expensive edge surface, not as the default memory or database.

## Core rule

Spend the fewest paid search calls needed to get to stable identifiers, then pivot to cheaper direct reads.

Priority order:
1. local memory or prior notes
2. exact/direct lookups by id, username, list id, or known handle
3. one narrow discovery search if needed
4. direct follow-up reads only

## Default operating policy

- Treat broad search as expensive.
- Default to one discovery search unless the user clearly wants wider exploration.
- Keep `max_results` small by default, usually 5, and only raise it when there is a concrete reason.
- Prefer exact quoted phrases or 1-3 distinctive terms over exploratory keyword piles.
- Avoid parallel search bursts unless the upside clearly justifies the spend.
- If a first search is noisy, tighten once, not five times.
- Cache useful identifiers in local notes or memory when they are likely to matter again.

## Cheapest tool order

Prefer these patterns when possible:

### 1. Exact account lookup
Use direct user lookup first.

Examples:
- `getUsersByUsername`
- `getUsersById`
- `getUsersByUsernames`

### 2. Exact post lookup
Use exact post reads when a URL or id is already known.

Examples:
- `getPostsById`
- `getPostsByIds`

### 3. Read from a known account
If the likely source is known, read that account instead of searching the whole network.

Examples:
- `getUsersPosts`
- `getUsersMentions`
- `getUsersOwnedLists`
- `getUsersFollowedLists`

### 4. Use one discovery search only when needed
Use search only to discover unknown accounts/posts/topics.

Examples:
- `searchPostsRecent`
- `searchUsers`
- `searchNews`

After discovery, pivot immediately to ids/usernames and stop searching.

## Query discipline

### Good
- one quoted phrase
- one exact username
- one concrete setup name
- one specific ticker plus one setup term

### Bad
- several broad synonyms in one request
- repeated reformulations of the same vague question
- high-result fishing without a plan
- multiple search queries launched at once just to browse

## Cost-aware workflows

### Find one good post on a topic
1. Run one narrow `searchPostsRecent` query.
2. Keep `max_results` at 5 or less.
3. Pick the best candidate quickly.
4. Save the post id and author id.
5. Use direct reads from there.

### Research an account
1. Use `getUsersByUsername`.
2. Use `getUsersPosts`.
3. Only use search if the handle is unknown.

### Track a theme over time
1. Identify 5-20 relevant accounts once.
2. Store handles in local notes or memory.
3. Read those accounts directly on future passes.
4. Re-run network search only occasionally.

### Validate docs or endpoint behavior
Prefer X docs MCP over paid search across live posts when the need is API/auth/tooling truth rather than social sentiment.

## When to spend more
Spend extra only when one of these is true:
- the user explicitly wants broad discovery
- the user asks for multiple candidates or a landscape scan
- the first narrow query genuinely fails
- the value of better coverage clearly outweighs the extra API cost

When spending more, say so briefly.

## Good answer framing
When cost matters, be explicit and short:
- what was searched
- how many searches were used
- what identifiers were found
- what should be cached for next time

## Local operating principle
On this machine, X should evolve toward:
- one-time discovery
- local watchlists and cached ids
- direct reads for repeat work
- X as ingestion, not as the live database for every step

## References

Read `references/cost-playbook.md` when you need concrete examples of cheap-vs-expensive X workflows.
