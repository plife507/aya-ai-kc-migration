# X Cost Playbook

## Goal

Minimize paid X/XMCP search usage while preserving answer quality.

## Cheap vs expensive

### Cheap
- `getUsersByUsername`
- `getUsersById`
- `getPostsById`
- `getPostsByIds`
- `getUsersPosts`
- `getUsersMentions`
- docs lookup through X docs MCP

### Expensive
- repeated `searchPostsRecent`
- broad exploratory discovery
- multiple parallel search passes
- high `max_results` without a concrete extraction plan

## Standard defaults

- Use at most 1 discovery search for a normal request.
- Default `max_results` to 5.
- Raise to 10 only when there is a stated reason.
- Avoid parallel search unless the request is explicitly broad.
- After finding a candidate, switch to direct reads.

## Examples

### User asks: "Find me a trading strategy on X"

Bad approach:
- run several broad searches
- try multiple synonyms
- inspect many low-quality candidates

Better approach:
1. run one narrow search for a concrete setup name or quoted phrase
2. inspect up to 5 results
3. choose one candidate
4. return the strategy with a note that broader exploration would cost more

### User asks: "What is @XDevelopers saying about auth?"

Cheap approach:
1. `getUsersByUsername("XDevelopers")`
2. `getUsersPosts(user_id)`
3. optionally use docs MCP for exact auth documentation

### User asks: "Read this X post"

Cheapest approach:
1. parse id from URL
2. use `getPostsById`
3. do not search

### User asks: "Who should I follow for ORB setups?"

Cost-aware approach:
1. one search to discover candidates
2. save usernames
3. return the shortlist
4. next time read those usernames directly

## Escalation rule

If one narrow search fails, do at most one refinement before stopping and explaining the tradeoff.

## Caching guidance

Store when useful:
- usernames
- user ids
- post ids
- list ids
- recurring topical watchlists
- which query worked well for discovery

## Answer pattern

Use short language like:
- "I kept this to one X search, then switched to direct reads."
- "I found 3 candidate accounts and saved the handles for cheaper follow-up next time."
- "I avoided broad search to keep API cost down."
