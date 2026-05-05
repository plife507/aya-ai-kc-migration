# Repo Creation Policy

## Quick rule

Use the smallest durable boundary that fits the work.

- if it is just support work, notes, config, or a one-off, use **no repo**
- if it is exploratory and may become real, use a **scratch workspace**
- if it belongs to a current system, use the **existing repo**
- if it has its own real identity and lifecycle, create a **new repo**

## The four outcomes

- `NO_REPO_NEEDED`
- `USE_EXISTING_REPO`
- `CREATE_NEW_REPO`
- `START_IN_EXISTING_REPO_AND_REEVALUATE`

## 1) NO_REPO_NEEDED

Use this when the work does not need long-term software ownership.

Examples:
- local machine config
- `~/.claude` edits
- OpenClaw config/workspace files
- policy docs, notes, references
- tiny one-off scripts
- temporary diagnostics
- short research spikes

Rule of thumb:
If it does not need real version history, collaboration, deployment, reuse, or ongoing maintenance, it probably does not need a repo.

## 2) Scratch workspace, not scratch repo

Default to a **scratch folder**, not a permanent junk-drawer repo.

Recommended shape:
- `~/Projects/_scratch/notes/`
- `~/Projects/_scratch/code/`
- `~/Projects/_scratch/tmp/`

Use `_scratch` for:
- rough experiments
- temporary extracted files
- prototypes with unclear destination
- quick tests before deciding the real home

Important:
`_scratch` is non-canonical. Nothing important should live there for long.

## 3) USE_EXISTING_REPO

Use the existing repo when the work clearly belongs to that system.

Signals:
- it is a feature or fix for the current product
- it depends tightly on that repo's models, runtime, or deploy flow
- it exists only to support that repo
- splitting it out would add overhead without clarity
- it would not make sense as a standalone project

Examples:
- adapters
- internal tooling for that repo
- migrations
- scripts used only by that repo
- repo-local `.claude` behavior

## 4) CREATE_NEW_REPO

Create a new repo when the work is a real standalone thing.

Signals:
- it has its own mission or product boundary
- it can run or deploy independently
- it needs its own README, TODO, docs, and issue history
- it may be reused across multiple projects
- it has its own config, secrets, or runtime boundary
- it would still make sense if the parent repo disappeared

## 5) START_IN_EXISTING_REPO_AND_REEVALUATE

Use this when the work is exploratory but already leans toward an existing system.

Start under a clear boundary such as:
- `experimental/`
- `tools/`
- `scripts/`
- `internal/`
- `adapters/`

Promote it later only if it earns a separate identity.

## Promotion triggers

Move something out of scratch or out of an existing repo when it starts needing:
- separate release cadence
- separate deployment
- separate ownership or access control
- reuse by other repos
- a different risk boundary
- significantly different docs, TODOs, or gates than the host repo

## Anti-fragmentation rule

Do not create a new repo just because:
- the folder is getting bigger
- the task feels important
- the code is new
- an agent is working on it
- it might maybe become standalone later

New repos should reduce confusion, not create more of it.

## Claude routing rule

Before deep implementation, decide the boundary first.

### Call Claude with no repo
For:
- config work
- workspace docs
- references
- one-off diagnostics
- support material

### Call Claude in an existing repo
For:
- real feature/fix work
- repo-owned tooling
- changes tied to that repo's tests, deploy flow, or docs

### Create a new repo before calling Claude deeply
For:
- a standalone app, service, CLI, library, or worker with its own lifecycle

### Use scratch before deciding
For:
- prototypes and unclear experiments
- then either discard, move into an existing repo, or promote to a new repo

## Default preference

Prefer fewer, clearer repos.

A new repo should be justified by a real boundary, not by vibes.
