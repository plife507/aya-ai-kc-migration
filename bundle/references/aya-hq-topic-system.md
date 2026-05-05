# Aya HQ Topic System

## Scope
Telegram group: `Aya HQ` (`-1003989941314`)

This group is the main Telegram home for Aya, split into four forum topics.

## Topic files
Use the topic-specific files directly:

- `references/topic-hq.md`
- `references/topic-kc.md`
- `references/topic-trade.md`
- `references/topic-life.md`

## Simple routing rule
- Aya/system/machine/config work -> HQ
- KC work -> KC
- TRADE system work -> TRADE
- personal/life context -> LIFE

## Runtime routing

As of 2026-04-24, live OpenClaw routing is explicit:

- Telegram DM from Nathan (`7275500887`) -> `main`
- Aya HQ topic `1` -> `main`
- Aya HQ topic `3` -> `kc`
- Aya HQ topic `5` -> `main`
- Aya HQ topic `7` -> `main`
- Slack `#pp-dispatch-mgmt` (`C08CTUF1T7C`) -> `kc`
- Slack `#ops-frontstage` (`C07QEEN75EU`) -> `kc`

Old mixed `main`/`kc` sessions can remain on disk. Treat live route resolution and fresh inbound messages as the source of truth.

## Runtime note
Verified topic separation exists at the Telegram session level. Keep the docs clean and topic-specific instead of storing all lane guidance in this umbrella file.
