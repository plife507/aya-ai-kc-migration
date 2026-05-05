# Aya web search workflow

## Default provider

Aya's default OpenClaw web search provider on this machine is now **Tavily**.

Use:

- `web_search` for normal quick discovery
- Tavily-native search/extract paths when deeper controls or content extraction are needed

## Current posture

- Tavily is configured as the default `tools.web.search.provider`
- the Tavily plugin is enabled
- Tavily is allowlisted in `plugins.allow`
- the live API key stays in local OpenClaw config and should not be committed into the repo

## Routing rule

### Use `web_search` when

- you need fast web discovery
- you want titles, URLs, and snippets
- you are still narrowing the search space

### Use Tavily-native capabilities when

- you need domain filtering
- you need deeper search controls
- you want AI-answer style search summaries
- you want targeted extraction from URLs

## Safety

- do not commit the raw live OpenClaw config
- do not paste the live Tavily key into repo files
- if the key was exposed in chat, treat rotation as later hygiene work
