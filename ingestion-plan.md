# AYA-AI Efficient Ingestion Plan

## Purpose

This adapts the migration handoff into an ingestion-ready plan for building AYA-AI's business memory and operating corpus.

The goal is not to ingest every file. The goal is to ingest the smallest high-signal corpus that lets AYA-AI operate KC workflows correctly, then keep runtime systems of record connected for live truth.

## Source Roots

Primary OpenClaw root:

- `/home/aya/.openclaw`

Primary workspace:

- `/home/aya/.openclaw/workspaces/agents/main`

Shared business roots:

- `/home/aya/.openclaw/workspaces/shared/docs`
- `/home/aya/.openclaw/workspaces/shared/kc-vault`
- `/home/aya/.openclaw/workspaces/shared/Projects`

Global skills:

- `/home/aya/.openclaw/skills`

Standalone Jobber repo:

- `/home/aya/.openclaw/workspaces/shared/Projects/jobber`

## Ingestion Strategy

Use four passes.

### Pass 1: Identity And Operating Rules

Purpose:

- Teach AYA-AI who it is, who it serves, what it should avoid, and how KC workflows are governed.

Ingest first:

- `workspaces/agents/main/AGENTS.md`
- `workspaces/agents/main/SOUL.md`
- `workspaces/agents/main/USER.md`
- `workspaces/agents/main/IDENTITY.md`
- `workspaces/agents/main/TOOLS.md`
- `workspaces/agents/main/TODO/TODO.md`
- `openclaw.example.json`
- `plugins/installs.json`
- `npm/package.json`

Do not ingest:

- `openclaw.json` as normal corpus. Treat it as sensitive configuration. Use `openclaw.example.json` for general structure.
- Personal memory outside the KC business boundary.

### Pass 2: Business Memory And World Book

Purpose:

- Preserve KC-specific operating knowledge without mixing in runtime logs, session databases, or personal data.

Ingest:

- `workspaces/agents/main/memory/*.md`
- `workspaces/shared/kc-vault/**/*.md`
- `workspaces/shared/docs/**/*.md`

Skip:

- `workspaces/agents/main/memory/.dreams/`
- `workspaces/agents/main/memory/dreaming/`
- Runtime memory databases under `/home/aya/.openclaw/memory/`

### Pass 3: Workflow Skills And Runbooks

Purpose:

- Preserve exact workflow behavior, safety gates, scripts, mappings, and operator tips.

Ingest:

- `skills/**/*.md`
- `workspaces/agents/main/skills/gog/SKILL.md`
- High-value skill references under:
  - `skills/kc-pp-job-costing/references/`
  - `skills/jobber-cli-v3-operator/references/`
  - `skills/kc-pp-sync/references/`
  - `skills/kc-pp-sync-operator/references/`
  - `skills/kc-cloud-ops/references/`

Include JSON mapping files only when they are explicit non-secret operational mappings, such as:

- `skills/kc-pp-job-costing/references/pp-companycam-assignments.json`

Skip generated caches, package folders, logs, and token files.

### Pass 4: Project Metadata

Purpose:

- Preserve enough project structure for developers and operators to reconnect systems without ingesting credentials.

Ingest from `workspaces/shared/Projects/jobber`:

- `README.md`
- `CLAUDE.md`
- `SECRETS.md`
- `TODO.md`
- `.env.example`
- `.agents/**`
- `.codex/**`
- `jobber-cli-v3/**/*.md`
- `oauth/**/*.md`
- `scripts/**/*.md`

Do not ingest:

- `.env`
- `tokens/`
- OAuth token JSON
- Runtime databases
- Build outputs

## Hard Exclusions

Exclude these paths completely from ingestion bundles unless deliberately restoring runtime state:

```text
/home/aya/.openclaw/secrets/
/home/aya/.openclaw/agents/
/home/aya/.openclaw/memory/
/home/aya/.openclaw/tasks/
/home/aya/.openclaw/cron/runs/
/home/aya/.openclaw/delivery-queue/
/home/aya/.openclaw/session-delivery-queue/
/home/aya/.openclaw/lcm.db*
/home/aya/.openclaw/lcm-files/
/home/aya/.openclaw/backups/
/home/aya/.openclaw/workspaces/agents/main/memory/.dreams/
/home/aya/.openclaw/workspaces/agents/main/memory/dreaming/
node_modules/
.venv/
.cache/
.git/
```

## Metadata To Attach Per Document

Each ingested document should carry metadata so retrieval can rank it correctly.

Recommended fields:

```json
{
  "source_root": "/home/aya/.openclaw",
  "relative_path": "workspaces/agents/main/AGENTS.md",
  "corpus": "aya-ai-kc",
  "domain": "identity|memory|skill|runbook|project|config-template",
  "department": "hq|pp|ops|finance|sales|marketing|reporting|shared",
  "priority": 1,
  "sensitive": false,
  "system_of_record": false
}
```

Priority guide:

- `1`: identity, safety rules, Phase 1 workflow skills, current runbooks
- `2`: KC memory, KC vault, docs, core project metadata
- `3`: supporting references, older daily notes, Phase 2 planning
- `4`: archived context kept for recall but not default retrieval

## Chunking Rules

Use structure-aware chunking.

- Split Markdown by headings.
- Keep heading path in chunk metadata.
- Target 600-1,200 tokens per chunk.
- Allow up to 1,800 tokens for checklists or command examples that lose meaning when split.
- Keep code blocks with their surrounding explanation.
- Do not split JSON mapping files by arbitrary byte count; ingest as one document if small, or by top-level key groups if large.
- Deduplicate identical symlinked content by canonical realpath and checksum.

## Retrieval Bias

For AYA-AI runtime retrieval:

- Prefer current `AGENTS.md`, `TOOLS.md`, and active skill docs over old daily memory.
- Prefer skills and runbooks for "how do I do this?" questions.
- Prefer live system lookups for Jobber, CompanyCam, Slack, Sheets, and Google Cloud state.
- Use memory for business context and prior decisions, not as a source of truth for mutable records.

## Secret Rehydration

Secrets must be restored outside the ingestion corpus.

Canonical secret roots:

```text
/home/aya/.openclaw/secrets/.env
/home/aya/.openclaw/secrets/jobber_tokens.json
/home/aya/.openclaw/secrets/gog/
```

Rehydrate via restricted files, Secret Manager, or the target OpenClaw secret system. Never embed secret contents in vector indexes, summaries, docs, or migration bundles.

## Validation Checklist

Before handing the corpus to the ingestion builder:

- [ ] Confirm no path under `secrets/` is included.
- [ ] Confirm no `.env`, token JSON, credential JSON, keyring, cache, DB, or session log is included.
- [ ] Confirm symlinks are recorded but not followed into excluded paths.
- [ ] Confirm `openclaw.example.json` is included and `openclaw.json` is excluded or redacted.
- [ ] Confirm `MEMORY.md` inclusion is business-safe for the dedicated KC AYA-AI instance.
- [ ] Confirm Phase 1 skills are tagged priority `1`.
- [ ] Confirm every chunk has `relative_path`, `domain`, `department`, and `priority`.

## Suggested Output Bundle

Recommended bundle shape:

```text
aya-ai-ingestion-bundle/
  manifest.json
  corpus/
    identity/
    memory/
    kc-vault/
    docs/
    skills/
    projects/
  reports/
    excluded-paths.txt
    skipped-sensitive-files.txt
    checksums.json
    symlinks.json
```

The builder should be able to ingest `manifest.json` first, then read only the listed corpus files.
