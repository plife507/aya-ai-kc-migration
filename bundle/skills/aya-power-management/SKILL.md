---
name: aya-power-management
description: Use when Nathan asks Aya to dim, brighten, boost performance, change local power profile, turn displays off/on, or operate the local Razer keyboard wake lighting. Routes through the canonical AYA-CLAW power scripts: `scripts/aya-dim`, `scripts/aya-bright`, and `scripts/aya-boost`.
---

# Aya Power Management

Use this skill for local power-state requests on Nathan's Aya machine.

## Canonical commands

Run from `/home/plife507/AYA-CLAW`:

```bash
scripts/aya-dim
scripts/aya-bright
scripts/aya-boost
```

Global PATH symlinks also exist in `/home/plife507/.local/bin`:

```bash
aya-dim
aya-bright
aya-boost
```

Deprecated compatibility aliases:

```bash
scripts/aya-sleep
scripts/aya-wakeup
```

Dry-run variants:

```bash
scripts/aya-dim --dry-run
scripts/aya-bright --dry-run
scripts/aya-boost --dry-run
```

Shared helper:

```bash
scripts/aya-power-common.sh
```

## Behavior

- `aya-dim`: sets `powerprofilesctl` to `power-saver`, marks keyboard wake state, tries to turn the Razer keyboard light off, and turns X11 displays off with `xset`.
- `aya-bright`: sets `powerprofilesctl` to `balanced`, restores keyboard lighting, clears the keywake flag, and nudges X11 displays back on.
- `aya-boost`: sets `powerprofilesctl` to `performance`.
- Deprecated aliases: `aya-sleep` maps to `aya-dim`; `aya-wakeup` maps to `aya-bright`. Prefer the dim/bright names everywhere because "sleep" and "wake" are overloaded with chat/session behavior.

## Operating rules

1. For inspection, validation, or "check" requests, run `bash -n` plus the relevant `--dry-run`.
2. For direct commands like "Aya-dim", "Aya-bright", or "Aya-boost", run the matching script directly.
3. If the request is ambiguous, prefer reporting the available commands and current state instead of changing power state.
4. Do not edit power scripts casually. Inspect the scripts first, then patch only the smallest necessary change.
5. If changing the scripts, verify with `bash -n` and all three dry-runs.

## Notes

- These scripts assume the local user is `plife507`, X11 display `:0`, and Xauthority at `/home/plife507/.Xauthority` unless overridden by environment variables.
- `aya-dim` may turn off displays, so only run it directly when Nathan clearly asks for the machine to dim or screen-off.
- Razer keyboard lighting operations are best-effort and should not block dim/bright behavior.
