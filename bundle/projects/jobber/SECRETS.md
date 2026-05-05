# Jobber local secret wiring

## Source of truth

Preferred canonical locations:
- `~/.secrets/aya/jobber.env`
- additional OAuth-specific local files may remain outside git when required by tooling

## Repo contract

- `.env.example` documents expected variables
- local `.env` may exist for runtime convenience
- repo is not the source of truth for live credentials

## Approved wiring methods

- symlink `.env` -> `~/.secrets/aya/jobber.env` (current live method)
- symlink `oauth/.env` -> `~/.secrets/aya/jobber-oauth.env` (current live method)
- generated/copied local `.env`
- direct tool/service reference to canonical secret files where supported

## Rule

Keep OAuth/token caches out of git and document any special runtime file expectations here.
