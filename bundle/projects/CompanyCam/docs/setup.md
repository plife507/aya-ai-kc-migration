# CompanyCam Setup

## What Nathan Needs To Do

1. Sign in to CompanyCam.
2. Generate an API access token from the CompanyCam app.
3. Do not paste the token into Telegram or Slack.
4. Put the token into the local project file:

```bash
cd /home/plife507/Projects/CompanyCam
cp .env.example .env
```

Then edit `.env` so it contains:

```bash
COMPANYCAM_API_TOKEN=your-token-here
```

## First Verification

Run:

```bash
npm install
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- token check --json
```

The first verification is read-only. It confirms:

- API token works.
- Current CompanyCam company is visible.
- Current CompanyCam user is visible.

Additional read-only checks:

```bash
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- projects list --json
COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env npm run dev -- checklists list --json
```

The older Python smoke check remains available at `scripts/companycam_check.py`.

## Work Process Direction

The CompanyCam piece should connect to the KC workflow this way:

1. Jobber/HeyPros gives us the job identity.
2. CompanyCam gives us the project/photos/documentation side.
3. Preferred Partner assignment should be mapped carefully:
   - CompanyCam may represent this as assigned users, collaborators, project labels, or another internal KC convention.
   - We need to inspect the actual CompanyCam account data before choosing the write path.
4. Until that mapping is verified, user assignment should be confirmed by exact CompanyCam user id before writing.

## Tomorrow Workflow

Use `docs/tomorrow-use.md` for the first live run. The short path is:

1. Match/select the project album, not the jobwalk album.
2. Confirm the exact project id, user id, and checklist template id with Nathan.
3. Dry-run `projects assign-user` and `projects apply-checklist`.
4. Run each approved live write with `COMPANYCAM_WRITES_ENABLED=1` for that one command only.

## Write Gate

Do not create, update, assign, tag, comment, upload, archive, delete, invite, or create webhooks without explicit approval for the exact action.

Live project creation, project title update, user assignment, and checklist creation require `COMPANYCAM_WRITES_ENABLED=1` for the single invocation.
