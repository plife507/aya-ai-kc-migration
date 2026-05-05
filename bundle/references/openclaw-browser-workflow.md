# Aya browser workflow

## Principle

Aya should use browser capability through OpenClaw directly.

The default browser architecture is hybrid:

- **managed isolated browser** for simple and repeatable work
- **live attached browser** for session-bound or higher-complexity work

## Routing

### Use managed browser first when

- task is simple
- no login is needed
- isolation is better
- repeatability matters

### Use live attached browser first when

- login or MFA is needed
- real cookies/session state matter
- Nathan wants visible collaboration
- the managed browser lane is unhealthy

## Escalation

1. managed browser
2. live attached browser
3. node-host or remote CDP if browser placement is wrong
4. desktop control only if browser automation is insufficient and approved

## Current host note

Right now the policy is clear, but only the live attached lane looks like the near-term reliable route. The managed lane is configured but still needs CDP startup reliability work.

## Skill

Primary skill file:

- `/home/plife507/AYA-CLAW/skills/openclaw-browser-operator/SKILL.md`

Host-specific reference:

- `/home/plife507/AYA-CLAW/skills/openclaw-browser-operator/references/hybrid-browser-workflow.md`
