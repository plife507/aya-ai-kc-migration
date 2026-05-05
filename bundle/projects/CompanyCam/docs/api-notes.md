# API Notes

## Official Sources

- Developer docs: https://docs.companycam.com/docs/welcome
- Core API overview: https://docs.companycam.com/docs/overview-1
- Getting started: https://docs.companycam.com/docs/getting-started
- OAuth guide: https://docs.companycam.com/docs/oauth
- Webhooks guide: https://docs.companycam.com/docs/webhooks-1
- Rate limits: https://docs.companycam.com/docs/rate-limits
- Current user header: https://docs.companycam.com/docs/defining-the-current-user
- API reference: https://docs.companycam.com/reference
- OpenAPI YAML: https://github.com/CompanyCam/openapi-spec/blob/main/openapi.yaml
- Raw OpenAPI YAML: https://raw.githubusercontent.com/CompanyCam/openapi-spec/main/openapi.yaml

## Confirmed From Docs

- Base URL: `https://api.companycam.com/v2`
- API style: REST Core API for core CompanyCam data such as projects and photos.
- Auth header: `Authorization: Bearer <token>`.
- For KC/internal use, a directly generated access token is likely enough to start read-only testing.
- OAuth is required for partner/public integrations.
- OAuth scopes listed by CompanyCam: `read`, `write`, `destroy`.
- OAuth token endpoint: `https://app.companycam.com/oauth/token`.
- OAuth access tokens expire; refresh tokens must be stored and rotated when refreshed.
- API access is available on Pro, Premium, and Elite plans.

## Likely KC Integration Patterns

The official overview examples map well to KC workflows:

- Create or match CompanyCam projects from Jobber/HeyPros CRM/job records.
- Sync CompanyCam photos back to job management records.
- Subscribe to webhook events when photos are tagged, then route those updates into KC operations workflows.

Keep all creation, update, delete, webhook, tag, and photo sync behavior behind explicit write approval until the exact mapping is proven.

## Rate Limits

CompanyCam docs list per-minute limits by HTTP method:

- `GET`: 240 calls/min
- `POST`: 100 calls/min
- `PUT`: 100 calls/min
- `DELETE`: 100 calls/min

Implement retry/backoff before any polling or sync job.

## Core Endpoint Areas

Relevant paths in the current OpenAPI spec include:

- Company/user identity: `/company`, `/users/current`, `/users`, `/users/{id}`
- Projects: `/projects`, `/projects/{id}`, archive/restore, assigned users, labels, comments, documents, checklists, invitations, collaborators, notepad
- Photos: `/photos`, `/photos/{id}`, `/projects/{project_id}/photos`, photo tags, comments, descriptions
- Checklists: `/checklists` lists all checklists sorted by last updated; query params include `page`, `per_page`, and `completed`.
- Tags and groups: `/tags`, `/groups`
- Webhooks: `/webhooks`, `/webhooks/{id}`
- Checklist templates: `/templates/checklists`

## Webhooks

CompanyCam webhooks can subscribe to project/photo/comment/document/video/checklist events. They POST to the configured URL and expect HTTP `200`; non-200 responses retry with exponential backoff up to 10 attempts, and a webhook with more than 25 total errors may be disabled.

Useful scopes for KC likely include:

- `project.created`
- `project.updated`
- `photo.created`
- `photo.tag_added`
- `photo.description_updated`
- `comment.created`
- `document.created`

## Current User / Attribution

For some write endpoints, CompanyCam supports designating the acting/creator user with an `X_COMPANYCAM_USER` / `X-CompanyCam-User` email header. Treat this as write-path behavior only; verify exact casing against the endpoint in the OpenAPI spec before use.

## KC First Workflow Notes

Best first read-only proof:

1. Confirm token works with `GET /company` and `GET /users/current`.
2. List projects with `GET /projects` using conservative pagination.
3. List checklists with `GET /checklists` using conservative pagination.
4. Test project/photo lookup with `GET /projects/{id}` and `GET /projects/{project_id}/photos`.
5. Do not upload, update, tag, comment, archive, delete, create webhooks, or alter assignments without explicit approval.

## Local Environment

Expected local secret:

```bash
COMPANYCAM_API_TOKEN=
```

Do not commit real credentials.
