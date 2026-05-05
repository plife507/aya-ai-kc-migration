# kc-pp-sync local secret wiring

## Source of truth

Preferred canonical location:
- `~/.secrets/aya/kc-pp-sync.env`

## Repo contract

- `.env.example` documents expected variables
- local `.env.local` may exist for runtime convenience
- repo is not the source of truth for live credentials

## Approved wiring methods

- symlink `.env.local` -> `~/.secrets/aya/kc-pp-sync.env` (current live method)
- generated/copied local `.env.local`
- service/deploy tooling may also read from canonical env material outside git

## Rule

Any change to runtime env expectations should update `.env.example` and this note.
