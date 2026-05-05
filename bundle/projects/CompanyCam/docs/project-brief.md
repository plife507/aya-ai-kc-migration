# Project Brief

## Working Name

CompanyCam

## Problem

KC needs a reliable way to work with CompanyCam data without depending on manual lookup and copy/paste workflows.

## First Workflow

- Take a Jobber job number/customer/address from Nathan.
- Match the CompanyCam project album by address/job details.
- Prefer the project album over a jobwalk album when both exist.
- Assign one approved CompanyCam user to the selected project.
- Apply one approved checklist template to the selected project.

## Later Workflow Candidates

- Pull project photos for documentation, QA, or customer follow-up.
- Create a clean internal summary of photos by project/date.
- Prepare future syncs to other KC systems.

## Constraints

- Treat all customer/project/photo data as private.
- Read-first until a write workflow is explicitly approved.
- Keep logs free of secrets and sensitive customer details.
- Prefer small scripts first; promote to service only after the workflow is stable.

## Decisions

- Runtime: TypeScript CLI with the original Python smoke scripts retained.
- Auth: local ignored `.env` with `COMPANYCAM_API_TOKEN`.
- First production workflow: project album lookup, user assignment, and checklist application.
- Writes: live writes stay gated per command with `COMPANYCAM_WRITES_ENABLED=1`.

## Open Decisions

- Whether this should stay standalone or connect to existing KC services.
- Final Preferred Partner to CompanyCam user mapping.
