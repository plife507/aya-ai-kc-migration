# Jobber job URL lookup notes

## Proven local example

API search result for Job #20371 returned:

- GraphQL id: `Z2lkOi8vSm9iYmVyL0pvYi8xNDE3NTQwMTk=`
- decoded form: `gid://Jobber/Job/141754019`
- browser URL id: `141754019`
- direct URL: `https://secure.getjobber.com/jobs/141754019`

## Important distinction

- `jobNumber` is the human-facing Jobber number
- GraphQL `id` is the encoded API identifier
- browser URL id is the final numeric segment inside the decoded GraphQL id

These are related but not interchangeable.

## Local tool path

Primary CLI:

`/home/plife507/Projects/jobber/jobber-cli-v3`

Typical lookup command:

```bash
cd /home/plife507/Projects/jobber/jobber-cli-v3
JOBBER_ENV_PATH=/home/plife507/Projects/jobber/.env \
JOBBER_OAUTH_SKIP_AUTHORIZE=1 \
yarn dev search jobs 20371 --json
```

Deprecated legacy path, do not use for current work:

`/home/plife507/Projects/KC/jobber-cli`

## Failure mode to remember

The main failure mode seen so far was stale Jobber OAuth, not missing schema support.
