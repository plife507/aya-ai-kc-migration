# Jobber Host Browser Flow

Purpose: define the Jobber website access path that fits the current AYA-CLAW system.

## Canonical model carried forward
Jobber website work should use a real browser session, not public scraping and not API mode by default.

Historical confirmed pattern:
- OpenClaw browser
- host-side browser on the machine running OpenClaw
- persistent profile, usually `openclaw`
- authenticated pages under `https://secure.getjobber.com/...`
- old VPS stack used Chromium with installed packages `chromium`, `chromium-common`, `chromium-sandbox`

## Current-machine finding
On this machine, the managed `openclaw` browser profile can reach Jobber, but it does **not** currently have enough trusted Jobber session state to pass through to the login/app flow cleanly.

Observed state on current host:
- managed profile path exists under `~/.openclaw/browser/openclaw/user-data`
- Jobber-related cookies exist only at challenge level
- no `cf_clearance` cookie was present when checked
- no authenticated Jobber app session was confirmed in the managed profile
- result: profile lands on Cloudflare security verification instead of the live Jobber app

## What this means
The old VPS recipe does **not** transfer 1:1 just by reusing the `openclaw` profile name.

The missing ingredient is not browser tooling. The missing ingredient is trusted/authenticated session state in the managed host profile.

## Adjusted flow for this system
### Primary path for Jobber website work
1. Prefer OpenClaw browser with `--browser-profile openclaw`
2. Treat that managed host profile as the desired long-term Jobber work surface
3. Do not assume it is ready until authenticated/trusted state is actually present

### Bootstrap rule
Before the managed host profile can become the durable Jobber lane on this machine, one of these must happen:
- seed a legitimate authenticated Jobber session into the managed host profile, or
- migrate still-valid host-browser profile/session state from the old environment, or
- use a live attached real-user browser lane temporarily until the managed host profile is trusted

### Temporary fallback
If the managed host profile is blocked at Cloudflare and Nathan's real local browser is available, use the live attached `user` lane for real Jobber work.

That fallback is for access continuity, not because it is the final preferred architecture.

## Operational stance
- Do not describe this as bypassing Jobber security
- Do not switch silently to scraping or API mode
- Do not assume browser reachability equals usable Jobber access
- Verify whether the profile has real authenticated session state before claiming Jobber browser readiness

## Practical one-line summary
For this machine, the correct Jobber target remains the managed host `openclaw` browser profile, but it still needs legitimate trusted/authenticated session state before it behaves like the old VPS Jobber lane.
