# Phase 0 - inventory and architecture approval

## Status

in progress

## Objective

Produce a full approved plan for Aya backup, secret storage, git hygiene, and recovery on this bare-metal machine before any migrations or automation changes are made.

## What this phase covers

- full inventory of current secret/storage locations
- classification of what belongs in git, local secret storage, app state, and external account stores
- target architecture for secret handling
- target architecture for nightly backups
- restore model for bare-metal failure recovery
- migration order with rollback safety

## Out of scope

- moving secrets
- editing services
- creating cron automation
- committing backup workflows
- deleting old secret files

## Findings already established

### Confirmed current secret/state surfaces

- `~/.openclaw/openclaw.json`
- `~/.openclaw/credentials/`
- `~/.openclaw/identity/`
- `~/AYA-CLAW/integrations/xmcp/.env`
- `~/Projects/KC/.env`
- `~/Projects/jobber/.env`
- `~/Projects/jobber/oauth/.env`
- `~/Projects/kc-pp-sync/.env.local`
- `~/Projects/TRADE/.env`
- mirrored/older `~/CODE/...` env files
- `~/.config/gcloud/...`
- `~/.config/gogcli/credentials.json`
- `~/.claude/.credentials.json`
- `~/.password-store`
- browser/session state under `~/.openclaw/browser/...`

### Confirmed repo posture

Most repo-local `.env` files appear to be gitignored already. This is good but still leaves secrets physically scattered.

### Confirmed local tool availability relevant to backup

Present:
- `rsync`
- `gpg`
- `tar`
- `zstd`
- `btrfs` binary present, but root filesystem is ext4, not btrfs

Not confirmed present:
- `restic`
- `borg`
- `rclone`
- `age`

### Confirmed service posture

User services relevant to Aya runtime:
- `openclaw-gateway.service`
- `xmcp.service`
- Aya helper user services already exist for keyboard behavior

## Proposed target architecture

### A. Clean git lane

Private git should contain:
- `AYA-CLAW`
- clean project repos
- code
- docs
- memory
- scripts
- systemd unit definitions that are safe to version
- `.env.example` files
- restore/runbook docs

Private git should not contain live secrets.

### B. Canonical secret root

Create a single local root for human-managed machine-readable secrets:

`~/.secrets/aya/`

Suggested layout:
- `openclaw.env`
- `xmcp.env`
- `kc.env`
- `jobber.env`
- `kc-pp-sync.env`
- `trade.env`
- `backup.env`
- `README.md` or `MAP.md` without secret values, only structure notes

### C. App-owned runtime state

Keep app-generated identity and state where they belong:
- `~/.openclaw/identity/`
- `~/.openclaw/credentials/`
- relevant browser/session state if continuity matters

### D. Per-project secret usage pattern

Each repo should own:
- schema
- examples
- docs
- a short local note describing how that repo receives secrets

Each repo should not be the source of truth for live credentials.

Preferred runtime pattern:
- local repo `.env` is symlinked/generated/sourced from `~/.secrets/aya/...`
- or service definitions point directly to `~/.secrets/aya/...`

Documentation rule per repo:
- add a short repo-local note such as `SECRETS.md`, `LOCAL_SETUP.md`, or equivalent section in README
- note should describe the secret file name/path contract, without containing secret values
- note should say whether the repo expects a symlink, generated file, direct `EnvironmentFile=`, or manual local `.env`

## Proposed phase plan

### Phase 1 - canonical secret layout creation

Create the secret root and define the file map.

#### Success barriers
- `~/.secrets/aya` exists with correct permissions
- no live service breaks
- written map exists describing which secret file feeds which runtime/project
- no secret values are committed to git

### Phase 2 - service and project secret migration

Migrate the highest-value/lowest-risk targets first.

Initial target order:
1. XMCP
2. OpenClaw-adjacent human-managed API keys
3. KC/Jobber project envs
4. TRADE/project envs

For each migrated repo/project:
- decide the runtime link method explicitly: symlink, generated local file, sourced shell/env file, or direct service `EnvironmentFile=`
- add/update repo-local documentation for that choice

#### Success barriers
- each migrated service/project still runs
- old and new paths are both documented during migration window
- each migrated repo has a local note describing how secrets are wired
- rollback path exists per target
- no secrets leaked into repo history

### Phase 3 - git backup lane for clean repos

Set up nightly commit/push for Aya-safe repos only.

#### Success barriers
- repo scope explicitly defined
- no live secrets tracked
- each included repo has clear local documentation about secret handling expectations
- nightly job runs successfully in dry-run/test mode
- push target verified

### Phase 4 - state backup lane for runtime and secrets

Back up non-git runtime state and canonical secret root.

Candidate scope:
- `~/.openclaw`
- `~/.config/systemd/user`
- `~/.secrets/aya`
- `~/.password-store`
- selected account credential stores if needed

#### Success barriers
- backup scope document exists
- backup command/script produces expected archive/output
- restore prerequisites documented
- exclusion list reviewed so junk/cache is not mixed in blindly

### Phase 5 - restore drill and verification

Optional future hardening step, not required for the current task closure.

#### Success barriers
- documented restore order exists
- optional only, unless Nathan later wants it

### Phase 6 - hardening and cleanup

After migration stabilizes, remove old duplication and tighten weak spots.

Candidate cleanup items:
- remove scattered old secret copies
- reduce insecure config flags where appropriate
- review browser/session state handling
- consider encryption later if needed

#### Success barriers
- duplicate secret copies removed or explicitly justified
- security audit warnings reviewed again
- final layout is simpler than before

## Risks

- moving secret paths can silently break services
- old duplicate secret files can create confusion about source of truth
- git backup automation can accidentally capture sensitive files if repo boundaries are not explicit
- browser/session continuity may be harder to restore than env-based credentials

## Rollback principle

No destructive cleanup until the new path is live, verified, and documented.

## Approval needed before execution

Nathan should approve:
- the target architecture
- the phase order
- whether private git remains non-secret-only
- whether phase 1 should begin with XMCP as the template migration

## Implementation progress

Completed so far:
- canonical secret root created at `~/.secrets/aya`
- secret map created at `~/.secrets/aya/MAP.md`
- architecture runbook created at `backups/runbooks/aya-backup-and-secrets-architecture.md`
- XMCP canonical secret file created at `~/.secrets/aya/xmcp.env`
- XMCP repo note added at `integrations/xmcp/SECRETS.md`
- XMCP user service updated to read from canonical secret path
- XMCP service restarted and verified healthy
- repo-local `SECRETS.md` notes added for KC, jobber, kc-pp-sync, and TRADE
- nightly state backup script created
- nightly git backup script created for `AYA-CLAW` lane only
- user systemd timers created and enabled for nightly git/state jobs
- one state backup archive created successfully

Not completed yet:
- restore drill is optional and explicitly not required now
- duplicate secret cleanup
- any later hardening Nathan wants beyond the current migration scope

## Done definition for Phase 0

Phase 0 is done only when:
- Nathan has reviewed the plan
- requested changes are incorporated
- a chosen execution order is confirmed
- phase 1 target(s) are explicitly authorized

Phase 0 result: done.

## Done definition for Phase 1

Phase 1 is done only when:
- canonical secret root exists with correct permissions
- map/docs exist
- no live service breaks occurred from foundational setup
- no secret values were committed to git during setup

Phase 1 result: done.
