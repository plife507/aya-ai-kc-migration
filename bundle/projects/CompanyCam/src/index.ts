#!/usr/bin/env node
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { asArray, CompanyCamClient, type JsonObject, type JsonValue, pickName } from "./core/client.js";
import { loadConfig, requireToken } from "./core/config.js";
import { readCsv, writeCsv } from "./core/csv.js";
import { CliError, errorToJson, EXIT_CODES } from "./core/errors.js";

const VERSION = "0.1.0";

const USER_FIELDS = [
  "id",
  "first_name",
  "last_name",
  "display_name",
  "email_address",
  "phone_number",
  "status",
  "user_role",
  "user_url",
  "company_id",
  "created_at",
  "updated_at",
];

const PP_FIELDS = [
  "companycam_user_id",
  "companycam_display_name",
  "companycam_email",
  "companycam_phone",
  "companycam_status",
  "companycam_role",
  "companycam_user_url",
  "pp_match_status",
  "pp_name",
  "pp_company_name",
  "pp_service_type",
  "pp_phone",
  "pp_email",
  "jobber_vendor_id",
  "heypros_profile_url",
  "preferred_partner_tier",
  "default_service_area",
  "notes",
];

interface ParsedArgs {
  command: string[];
  json: boolean;
  envPath?: string;
  options: Record<string, string | boolean>;
}

interface AddressTarget {
  input: string;
  query: string;
  address?: JsonObject;
  normalizedFull: string;
  normalizedLine1: string;
}

interface ProjectAddressMatch {
  id: string;
  name: string;
  projectUrl?: string;
  address?: JsonValue;
  matchType: "exact" | "line1";
  normalizedAddress: string;
  raw: JsonObject;
}

interface ProjectMatchResult {
  status: "none" | "matched" | "ambiguous";
  candidates: number;
  matches: ProjectAddressMatch[];
}

interface ChecklistTemplateSummary {
  id: string;
  name: string;
  description: string;
}

interface ChecklistPlanBase {
  template: ChecklistTemplateSummary;
}

type ChecklistPlan =
  | (ChecklistPlanBase & { action: "create-after-project-create" })
  | (ChecklistPlanBase & { action: "create-on-existing-project"; projectId: string })
  | (ChecklistPlanBase & { action: "force-create-on-existing-project"; projectId: string })
  | (ChecklistPlanBase & { action: "already-applied"; projectId: string; checklistId: string; checklistName: string });

interface SyncPlanBase {
  jobNumber: string;
  desiredName: string;
  matchStatus: ProjectMatchResult["status"];
  checklistPlan?: ChecklistPlan;
}

type SyncPlan =
  | (SyncPlanBase & { action: "create-project"; payload: JsonObject })
  | (SyncPlanBase & { action: "update-title"; project: ProjectAddressMatch; newName: string; currentName: string })
  | (SyncPlanBase & { action: "already-synced"; project: ProjectAddressMatch })
  | (SyncPlanBase & { action: "manual-review"; matches: ProjectAddressMatch[] });

async function main(): Promise<number> {
  const parsed = parseArgs(process.argv.slice(2));

  if (parsed.options.version === true) {
    printVersion();
    return EXIT_CODES.OK;
  }

  if (parsed.command.length === 0 || parsed.options.help === true) {
    printHelp();
    return EXIT_CODES.OK;
  }

  const [root, sub, id] = parsed.command;
  if (root === "version") {
    printVersion();
    return EXIT_CODES.OK;
  }

  const config = loadConfig(parsed.envPath);

  if (root === "status") {
    return output(parsed, {
      ok: true,
      command: "status",
      repoRoot: config.repoRoot,
      envPath: config.envPath,
      envPresent: existsSync(config.envPath),
      tokenConfigured: Boolean(config.token),
      writesEnabled: config.writesEnabled,
      baseUrl: config.baseUrl,
      timeoutMs: config.timeoutMs,
    });
  }

  if (root === "doctor") {
    return output(parsed, {
      ok: true,
      command: "doctor",
      repoRoot: config.repoRoot,
      envPath: config.envPath,
      envPresent: existsSync(config.envPath),
      tokenConfigured: Boolean(config.token),
      tokenSource: process.env.COMPANYCAM_API_TOKEN ? "environment" : config.token ? "env-file" : "missing",
      writesEnabled: config.writesEnabled,
      baseUrl: config.baseUrl,
      timeoutMs: config.timeoutMs,
      nodeVersion: process.version,
      headless: true,
    });
  }

  if (root === "token" && sub === "check") {
    const client = newClient(config);
    const company = await client.get("/company");
    const currentUser = await client.get("/users/current");
    return output(parsed, {
      ok: true,
      command: "token check",
      company: summarizeRecord(company),
      currentUser: summarizeRecord(currentUser),
    });
  }

  if (root === "users" && sub === "export") {
    const client = newClient(config);
    const users = await fetchAllUsers(client);
    users.sort((left, right) => pickName(left).localeCompare(pickName(right)));
    const exportDir = join(config.repoRoot, "exports");
    mkdirSync(exportDir, { recursive: true });
    const jsonPath = join(exportDir, "companycam_users.json");
    const csvPath = join(exportDir, "companycam_users.csv");
    writeFileSync(jsonPath, `${JSON.stringify(users, null, 2)}\n`, "utf-8");
    writeCsv(csvPath, USER_FIELDS, users.map(flattenUser));
    return output(parsed, {
      ok: true,
      command: "users export",
      users: users.length,
      active: users.filter((user) => user.status === "active").length,
      files: { json: jsonPath, csv: csvPath },
    });
  }

  if (root === "templates" && sub === "checklists" && (!id || id === "list")) {
    const client = newClient(config);
    const templates = await fetchChecklistTemplates(client);
    return output(parsed, { ok: true, command: "templates checklists list", count: templates.length, templates });
  }

  if (root === "projects" && sub === "list") {
    const client = newClient(config);
    const page = positiveIntOption(parsed, "page", 1);
    const perPage = positiveIntOption(parsed, "per-page", 25);
    const projects = await client.get("/projects", { page, per_page: perPage });
    return output(parsed, {
      ok: true,
      command: "projects list",
      page,
      perPage,
      projects,
    });
  }

  if (root === "projects" && sub === "create") {
    const payload = buildProjectCreatePayload(parsed);
    const creatorEmail = stringOption(parsed, "creator-email");
    const dryRun = parsed.options["dry-run"] === true;
    if (dryRun) {
      return output(parsed, {
        ok: true,
        command: "projects create",
        dryRun: true,
        writesEnabled: config.writesEnabled,
        payload,
        headers: creatorEmail ? { "X-CompanyCam-User": creatorEmail } : {},
      });
    }
    if (!config.writesEnabled) {
      throw new CliError(
        "Refusing live CompanyCam project create. Re-run with --dry-run or set COMPANYCAM_WRITES_ENABLED=1 for this command.",
        EXIT_CODES.WRITE_DISABLED,
        { payload },
      );
    }
    const client = newClient(config);
    const project = await client.post("/projects", payload, { "X-CompanyCam-User": creatorEmail });
    return output(parsed, { ok: true, command: "projects create", project });
  }

  if (root === "projects" && sub === "match") {
    const client = newClient(config);
    const target = buildAddressTarget(parsed);
    const match = await matchProjectsByAddress(client, target);
    return output(parsed, { ok: true, command: "projects match", target, ...match });
  }

  if (root === "projects" && sub === "sync-job") {
    const client = newClient(config);
    const dryRun = parsed.options["dry-run"] === true;
    const creatorEmail = stringOption(parsed, "creator-email");
    const jobNumber = requiredStringOption(parsed, "job-number");
    const jobTitle = requiredStringOption(parsed, "title");
    const checklistTemplate = await resolveChecklistTemplate(client, parsed);
    const target = buildAddressTarget(parsed);
    const match = await matchProjectsByAddress(client, target);
    const desiredName = buildJobProjectName(jobNumber, jobTitle);
    const plan = await buildSyncPlan(client, jobNumber, desiredName, target, match, checklistTemplate);

    if (dryRun) {
      return output(parsed, {
        ok: true,
        command: "projects sync-job",
        dryRun: true,
        writesEnabled: config.writesEnabled,
        target,
        plan,
      });
    }
    if (plan.action === "manual-review") {
      throw new CliError("CompanyCam project match is ambiguous; review candidate projects before writing.", EXIT_CODES.VALIDATION, plan);
    }
    if (!config.writesEnabled) {
      throw new CliError(
        "Refusing live CompanyCam job sync. Re-run with --dry-run or set COMPANYCAM_WRITES_ENABLED=1 for this command.",
        EXIT_CODES.WRITE_DISABLED,
        { plan },
      );
    }
    if (plan.action === "update-title") {
      const project = await client.put(`/projects/${encodeURIComponent(plan.project.id)}`, { name: plan.newName }, { "X-CompanyCam-User": creatorEmail });
      const checklist = await applyChecklistPlan(client, plan.checklistPlan, jsonObjectId(project), creatorEmail);
      return output(parsed, { ok: true, command: "projects sync-job", action: plan.action, project, checklist });
    }
    if (plan.action === "create-project") {
      const project = await client.post("/projects", plan.payload, { "X-CompanyCam-User": creatorEmail });
      const checklist = await applyChecklistPlan(client, plan.checklistPlan, jsonObjectId(project), creatorEmail);
      return output(parsed, { ok: true, command: "projects sync-job", action: plan.action, project, checklist });
    }
    const checklist = await applyChecklistPlan(client, plan.checklistPlan, plan.action === "already-synced" ? plan.project.id : undefined, creatorEmail);
    return output(parsed, { ok: true, command: "projects sync-job", action: plan.action, project: plan.project, checklist });
  }

  if (root === "projects" && sub === "get" && id) {
    const client = newClient(config);
    const project = await client.get(`/projects/${encodeURIComponent(id)}`);
    return output(parsed, { ok: true, command: "projects get", project });
  }

  if (root === "projects" && sub === "photos" && id) {
    const client = newClient(config);
    const page = positiveIntOption(parsed, "page", 1);
    const perPage = positiveIntOption(parsed, "per-page", 25);
    const photos = await client.get(`/projects/${encodeURIComponent(id)}/photos`, { page, per_page: perPage });
    return output(parsed, {
      ok: true,
      command: "projects photos",
      projectId: id,
      page,
      perPage,
      photos,
    });
  }

  if (root === "projects" && sub === "assigned-users" && id) {
    const client = newClient(config);
    const page = positiveIntOption(parsed, "page", 1);
    const perPage = positiveIntOption(parsed, "per-page", 100);
    const users = await client.get(`/projects/${encodeURIComponent(id)}/assigned_users`, { page, per_page: perPage });
    return output(parsed, {
      ok: true,
      command: "projects assigned-users",
      projectId: id,
      page,
      perPage,
      users,
    });
  }

  if (root === "projects" && sub === "assign-user" && id) {
    const projectId = id;
    const userId = requiredStringOption(parsed, "user-id");
    const creatorEmail = stringOption(parsed, "creator-email");
    const dryRun = parsed.options["dry-run"] === true;
    const path = `/projects/${encodeURIComponent(projectId)}/assigned_users/${encodeURIComponent(userId)}`;
    const headers = creatorEmail ? { "X-CompanyCam-User": creatorEmail } : {};
    if (dryRun) {
      return output(parsed, {
        ok: true,
        command: "projects assign-user",
        dryRun: true,
        writesEnabled: config.writesEnabled,
        method: "PUT",
        path,
        headers,
      });
    }
    if (!config.writesEnabled) {
      throw new CliError(
        "Refusing live CompanyCam user assignment. Re-run with --dry-run or set COMPANYCAM_WRITES_ENABLED=1 for this command.",
        EXIT_CODES.WRITE_DISABLED,
        { method: "PUT", path, headers },
      );
    }
    const client = newClient(config);
    const user = await client.put(path, {}, headers);
    return output(parsed, { ok: true, command: "projects assign-user", projectId, userId, user });
  }

  if (root === "projects" && sub === "apply-checklist" && id) {
    const client = newClient(config);
    const projectId = id;
    const creatorEmail = stringOption(parsed, "creator-email");
    const dryRun = parsed.options["dry-run"] === true;
    const forceNew = parsed.options["force-new"] === true;
    const checklistTemplate = await resolveRequiredChecklistTemplate(client, parsed);
    const plan = forceNew
      ? { action: "force-create-on-existing-project" as const, projectId, template: checklistTemplate }
      : await buildChecklistPlan(client, projectId, checklistTemplate);
    if (dryRun) {
      return output(parsed, {
        ok: true,
        command: "projects apply-checklist",
        dryRun: true,
        writesEnabled: config.writesEnabled,
        projectId,
        plan,
      });
    }
    if (!config.writesEnabled) {
      throw new CliError(
        "Refusing live CompanyCam checklist application. Re-run with --dry-run or set COMPANYCAM_WRITES_ENABLED=1 for this command.",
        EXIT_CODES.WRITE_DISABLED,
        { projectId, plan },
      );
    }
    const checklist = await applyChecklistPlan(client, plan, projectId, creatorEmail);
    return output(parsed, { ok: true, command: "projects apply-checklist", projectId, checklist });
  }

  if (root === "projects" && sub === "merge") {
    const sourceProjectId = requiredStringOption(parsed, "source-project-id");
    const targetProjectId = requiredStringOption(parsed, "target-project-id");
    const creatorEmail = stringOption(parsed, "creator-email");
    const dryRun = parsed.options["dry-run"] === true;
    const archiveEmptySource = parsed.options["archive-empty-source"] === true;
    const archivePath = `/projects/${encodeURIComponent(sourceProjectId)}/archive`;

    if (sourceProjectId === targetProjectId) {
      throw new CliError("Source and target projects must be different", EXIT_CODES.VALIDATION, { sourceProjectId, targetProjectId });
    }

    if (dryRun) {
      return output(parsed, {
        ok: true,
        command: "projects merge",
        dryRun: true,
        writesEnabled: config.writesEnabled,
        sourceProjectId,
        targetProjectId,
        apiMergeAvailable: false,
        action: archiveEmptySource ? "archive-empty-source" : "manual-web-merge-required",
        method: archiveEmptySource ? "PATCH" : undefined,
        path: archiveEmptySource ? archivePath : undefined,
        note: mergeCapabilityNote(),
      });
    }

    if (!archiveEmptySource) {
      throw new CliError(
        "CompanyCam Core API does not expose project merge. Use --archive-empty-source only for verified empty duplicates, or merge in the CompanyCam web app.",
        EXIT_CODES.VALIDATION,
        { sourceProjectId, targetProjectId, note: mergeCapabilityNote() },
      );
    }

    if (!config.writesEnabled) {
      throw new CliError(
        "Refusing live CompanyCam empty-source merge/archive. Re-run with --dry-run or set COMPANYCAM_WRITES_ENABLED=1 for this command.",
        EXIT_CODES.WRITE_DISABLED,
        { sourceProjectId, targetProjectId, method: "PATCH", path: archivePath },
      );
    }

    const client = newClient(config);
    const sourceProject = await client.get(`/projects/${encodeURIComponent(sourceProjectId)}`);
    const targetProject = await client.get(`/projects/${encodeURIComponent(targetProjectId)}`);
    const sourcePhotos = asArray(
      await client.get(`/projects/${encodeURIComponent(sourceProjectId)}/photos`, { page: 1, per_page: 1 }),
      `/projects/${sourceProjectId}/photos`,
    );
    const sourcePhotoCount = projectPhotoCount(sourceProject);

    if ((sourcePhotoCount !== undefined && sourcePhotoCount > 0) || sourcePhotos.length > 0) {
      throw new CliError(
        "Refusing to archive source project because it is not empty. Use the CompanyCam web merge tool so project content transfers correctly.",
        EXIT_CODES.VALIDATION,
        { source: summarizeProject(sourceProject), target: summarizeProject(targetProject), sourcePhotosChecked: sourcePhotos.length },
      );
    }

    const archivedSource = await client.patch(archivePath, {}, { "X-CompanyCam-User": creatorEmail });
    return output(parsed, {
      ok: true,
      command: "projects merge",
      action: "archive-empty-source",
      source: summarizeProject(sourceProject),
      target: summarizeProject(targetProject),
      archivedSource: summarizeProject(archivedSource),
      note: "Source project had no photos, so the duplicate was archived. For non-empty duplicates, use CompanyCam's web merge tool.",
    });
  }

  if (root === "checklists" && sub === "list") {
    const client = newClient(config);
    const page = positiveIntOption(parsed, "page", 1);
    const perPage = positiveIntOption(parsed, "per-page", 25);
    const completed = stringOption(parsed, "completed");
    const checklists = await client.get("/checklists", { page, per_page: perPage, completed });
    return output(parsed, {
      ok: true,
      command: "checklists list",
      page,
      perPage,
      checklists,
    });
  }

  if (root === "pp" && sub === "template") {
    const source = resolve(String(parsed.options.source || join(config.repoRoot, "exports", "companycam_users.csv")));
    const result = buildPpTemplates(config.repoRoot, source);
    return output(parsed, { ok: true, command: "pp template", ...result });
  }

  throw new CliError(`Unknown command: ${parsed.command.join(" ")}`, EXIT_CODES.VALIDATION);
}

function parseArgs(argv: string[]): ParsedArgs {
  const command: string[] = [];
  const options: Record<string, string | boolean> = {};
  let envPath: string | undefined;
  let json = false;

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--json") {
      json = true;
      continue;
    }
    if (arg === "--help" || arg === "-h") {
      options.help = true;
      continue;
    }
    if (arg === "--version" || arg === "-v") {
      options.version = true;
      continue;
    }
    if (arg === "--env") {
      const next = argv[index + 1];
      if (!next || next.startsWith("--")) {
        throw new CliError("--env requires a path", EXIT_CODES.VALIDATION);
      }
      envPath = next;
      index += 1;
      continue;
    }
    if (arg.startsWith("--env=")) {
      envPath = arg.slice("--env=".length);
      if (!envPath) {
        throw new CliError("--env requires a path", EXIT_CODES.VALIDATION);
      }
      continue;
    }
    if (arg.startsWith("--")) {
      const withoutPrefix = arg.slice(2);
      const [key, inlineValue] = withoutPrefix.split("=", 2);
      if (inlineValue !== undefined) {
        options[key] = inlineValue;
      } else if (argv[index + 1] && !argv[index + 1].startsWith("--")) {
        options[key] = argv[index + 1];
        index += 1;
      } else {
        options[key] = true;
      }
      continue;
    }
    command.push(arg);
  }

  return { command, json, envPath, options };
}

function newClient(config: ReturnType<typeof loadConfig>): CompanyCamClient {
  return new CompanyCamClient(requireToken(config), config.baseUrl, config.timeoutMs);
}

async function fetchChecklistTemplates(client: CompanyCamClient): Promise<ChecklistTemplateSummary[]> {
  return asArray(await client.get("/templates/checklists"), "/templates/checklists").map(summarizeChecklistTemplate);
}

function summarizeChecklistTemplate(template: JsonObject): ChecklistTemplateSummary {
  return {
    id: stringValue(template.id),
    name: stringValue(template.name),
    description: stringValue(template.description),
  };
}

async function resolveChecklistTemplate(
  client: CompanyCamClient,
  parsed: ParsedArgs,
): Promise<ChecklistTemplateSummary | undefined> {
  const requestedId = stringOption(parsed, "checklist-template-id");
  const requestedName = stringOption(parsed, "checklist-template-name");
  if (requestedId && requestedName) {
    throw new CliError("Use either --checklist-template-id or --checklist-template-name, not both", EXIT_CODES.VALIDATION);
  }
  if (!requestedId && !requestedName) {
    return undefined;
  }
  const templates = await fetchChecklistTemplates(client);
  if (requestedId) {
    const match = templates.find((template) => template.id === requestedId);
    if (!match) {
      throw new CliError(`Unknown checklist template id: ${requestedId}`, EXIT_CODES.VALIDATION, { available: templates });
    }
    return match;
  }
  const normalized = normalizeText(String(requestedName));
  const exact = templates.filter((template) => normalizeText(template.name) === normalized);
  if (exact.length === 1) {
    return exact[0];
  }
  const partial = templates.filter((template) => normalizeText(template.name).includes(normalized));
  if (partial.length === 1) {
    return partial[0];
  }
  throw new CliError("Checklist template name is missing or ambiguous", EXIT_CODES.VALIDATION, { requestedName, matches: partial, available: templates });
}

async function resolveRequiredChecklistTemplate(client: CompanyCamClient, parsed: ParsedArgs): Promise<ChecklistTemplateSummary> {
  const template = await resolveChecklistTemplate(client, parsed);
  if (!template) {
    throw new CliError("Provide --checklist-template-id or --checklist-template-name", EXIT_CODES.VALIDATION);
  }
  return template;
}

async function fetchAllUsers(client: CompanyCamClient): Promise<JsonObject[]> {
  const users: JsonObject[] = [];
  let page = 1;
  const perPage = 100;
  while (true) {
    const batch = asArray(await client.get("/users", { page, per_page: perPage }), `/users page ${page}`);
    if (batch.length === 0) {
      break;
    }
    users.push(...batch);
    if (batch.length < perPage) {
      break;
    }
    page += 1;
  }
  return users;
}

function jsonObjectId(value: JsonValue): string | undefined {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return undefined;
  }
  return stringValue(value.id);
}

function summarizeRecord(record: JsonValue): Record<string, unknown> {
  if (!record || typeof record !== "object" || Array.isArray(record)) {
    return { name: pickName(record) };
  }
  return {
    id: record.id,
    name: pickName(record),
    email: record.email || record.email_address,
  };
}

function summarizeProject(project: JsonValue): Record<string, unknown> {
  if (!project || typeof project !== "object" || Array.isArray(project)) {
    return { name: pickName(project) };
  }
  return {
    id: project.id,
    name: project.name,
    status: project.status,
    archived: project.archived,
    photoCount: project.photo_count,
    projectUrl: project.project_url,
    address: project.address,
  };
}

function projectPhotoCount(project: JsonValue): number | undefined {
  if (!project || typeof project !== "object" || Array.isArray(project)) {
    return undefined;
  }
  const value = project.photo_count;
  return typeof value === "number" ? value : undefined;
}

function mergeCapabilityNote(): string {
  return "CompanyCam's public Core API does not expose a full project merge endpoint. The CLI can archive a verified empty duplicate source; non-empty project merges must be completed in the CompanyCam web app so photos/files/reports/pages transfer correctly.";
}

function flattenUser(user: JsonObject): Record<string, unknown> {
  const first = stringValue(user.first_name);
  const last = stringValue(user.last_name);
  const displayName = `${first} ${last}`.trim() || stringValue(user.email_address) || stringValue(user.id);
  return {
    id: user.id,
    first_name: user.first_name,
    last_name: user.last_name,
    display_name: displayName,
    email_address: user.email_address,
    phone_number: user.phone_number,
    status: user.status,
    user_role: user.user_role,
    user_url: user.user_url,
    company_id: user.company_id,
    created_at: user.created_at,
    updated_at: user.updated_at,
  };
}

function buildPpTemplates(repoRoot: string, source: string): Record<string, unknown> {
  if (!existsSync(source)) {
    throw new CliError(`Missing source CSV: ${source}. Run users export first.`, EXIT_CODES.VALIDATION);
  }
  const users = readCsv(source);
  const fullRows = users.map(buildPpRow);
  const activeRows = users.filter((user) => user.status === "active").map(buildPpRow);
  const exportDir = join(repoRoot, "exports");
  const activePath = join(exportDir, "companycam_pp_mapping_template_active.csv");
  const fullPath = join(exportDir, "companycam_pp_mapping_template_full.csv");
  const readmePath = join(exportDir, "companycam_pp_mapping_template_README.md");

  writeCsv(activePath, PP_FIELDS, activeRows);
  writeCsv(fullPath, PP_FIELDS, fullRows);
  writeFileSync(readmePath, ppReadme(activeRows.length, fullRows.length), "utf-8");

  return {
    source,
    activeRows: activeRows.length,
    fullRows: fullRows.length,
    files: { active: activePath, full: fullPath, readme: readmePath },
  };
}

function buildProjectCreatePayload(parsed: ParsedArgs): JsonObject {
  const payload: JsonObject = { name: requiredStringOption(parsed, "name") };
  const address: JsonObject = {};
  addOptionalString(address, "street_address_1", stringOption(parsed, "street-address-1"));
  addOptionalString(address, "street_address_2", stringOption(parsed, "street-address-2"));
  addOptionalString(address, "city", stringOption(parsed, "city"));
  addOptionalString(address, "state", stringOption(parsed, "state"));
  addOptionalString(address, "postal_code", stringOption(parsed, "postal-code"));
  addOptionalString(address, "country", stringOption(parsed, "country"));
  if (Object.keys(address).length > 0) {
    payload.address = address;
  }

  const lat = numberOption(parsed, "lat");
  const lon = numberOption(parsed, "lon");
  if ((lat === undefined) !== (lon === undefined)) {
    throw new CliError("--lat and --lon must be provided together", EXIT_CODES.VALIDATION);
  }
  if (lat !== undefined && lon !== undefined) {
    payload.coordinates = { lat, lon };
  }

  const contact: JsonObject = {};
  addOptionalString(contact, "name", stringOption(parsed, "contact-name"));
  addOptionalString(contact, "email", stringOption(parsed, "contact-email"));
  addOptionalString(contact, "phone_number", stringOption(parsed, "contact-phone"));
  if (Object.keys(contact).length > 0) {
    if (!contact.name) {
      throw new CliError("--contact-name is required when contact email or phone is provided", EXIT_CODES.VALIDATION);
    }
    payload.primary_contact = contact;
  }

  return payload;
}

function buildAddressTarget(parsed: ParsedArgs): AddressTarget {
  const freeformAddress = stringOption(parsed, "address");
  const address = buildAddressPayload(parsed);
  const formatted = freeformAddress || formatAddress(address);
  if (!formatted) {
    throw new CliError("Provide --address or at least --street-address-1 for address matching", EXIT_CODES.VALIDATION);
  }
  const line1 = stringOption(parsed, "street-address-1") || formatted.split(",")[0]?.trim() || formatted;
  const query = line1 || formatted;
  return {
    input: formatted,
    query,
    address: Object.keys(address).length > 0 ? address : undefined,
    normalizedFull: normalizeAddress(formatted),
    normalizedLine1: normalizeAddress(line1),
  };
}

function buildAddressPayload(parsed: ParsedArgs): JsonObject {
  const address: JsonObject = {};
  addOptionalString(address, "street_address_1", stringOption(parsed, "street-address-1"));
  addOptionalString(address, "street_address_2", stringOption(parsed, "street-address-2"));
  addOptionalString(address, "city", stringOption(parsed, "city"));
  addOptionalString(address, "state", stringOption(parsed, "state"));
  addOptionalString(address, "postal_code", stringOption(parsed, "postal-code"));
  addOptionalString(address, "country", stringOption(parsed, "country"));
  return address;
}

async function matchProjectsByAddress(client: CompanyCamClient, target: AddressTarget): Promise<ProjectMatchResult> {
  const perPage = 25;
  const projects = asArray(await client.get("/projects", { page: 1, per_page: perPage, query: target.query }), "/projects address query");
  const allMatches = projects.flatMap((project) => projectAddressMatch(project, target));
  const exactMatches = allMatches.filter((match) => match.matchType === "exact");
  const matches = exactMatches.length > 0 ? exactMatches : allMatches;
  if (matches.length === 0) {
    return { status: "none", candidates: projects.length, matches };
  }
  if (matches.length === 1) {
    return { status: "matched", candidates: projects.length, matches };
  }
  return { status: "ambiguous", candidates: projects.length, matches };
}

function projectAddressMatch(project: JsonObject, target: AddressTarget): ProjectAddressMatch[] {
  const address = project.address;
  if (!address || typeof address !== "object" || Array.isArray(address)) {
    return [];
  }
  const addressLine1 = stringValue(address.street_address_1);
  const normalizedLine1 = normalizeAddress(addressLine1);
  const normalizedFull = normalizeAddress(formatAddress(address));
  const exact = Boolean(target.normalizedFull && normalizedFull === target.normalizedFull);
  const line1 = Boolean(target.normalizedLine1 && normalizedLine1 === target.normalizedLine1);
  const line1Compatible = Boolean(
    line1 &&
      ((target.address && addressComponentsMatch(address, target.address)) || (!target.address && target.input === target.query)),
  );
  if (!exact && !line1Compatible) {
    return [];
  }
  const id = stringValue(project.id);
  if (!id) {
    return [];
  }
  return [
    {
      id,
      name: stringValue(project.name),
      projectUrl: stringOptionFromValue(project.project_url),
      address,
      matchType: exact ? "exact" : "line1",
      normalizedAddress: normalizedFull,
      raw: project,
    },
  ];
}

function addressComponentsMatch(candidate: JsonObject, target: JsonObject): boolean {
  for (const key of ["street_address_2", "city", "state", "postal_code", "country"]) {
    const targetValue = stringValue(target[key]);
    if (targetValue && normalizeAddress(stringValue(candidate[key])) !== normalizeAddress(targetValue)) {
      return false;
    }
  }
  return true;
}

async function buildSyncPlan(
  client: CompanyCamClient,
  jobNumber: string,
  desiredName: string,
  target: AddressTarget,
  match: ProjectMatchResult,
  checklistTemplate?: ChecklistTemplateSummary,
): Promise<SyncPlan> {
  const base = { jobNumber, desiredName, matchStatus: match.status };
  if (match.status === "ambiguous") {
    return { ...base, action: "manual-review", matches: match.matches };
  }
  if (match.status === "none") {
    const payload: JsonObject = { name: desiredName };
    if (target.address) {
      payload.address = target.address;
    }
    const checklistPlan = checklistTemplate ? { action: "create-after-project-create" as const, template: checklistTemplate } : undefined;
    return { ...base, action: "create-project", payload, checklistPlan };
  }
  const project = match.matches[0];
  const checklistPlan = checklistTemplate ? await buildChecklistPlan(client, project.id, checklistTemplate) : undefined;
  if (project.name.includes(jobNumber)) {
    return { ...base, action: "already-synced", project, checklistPlan };
  }
  return { ...base, action: "update-title", project, currentName: project.name, newName: desiredName, checklistPlan };
}

async function buildChecklistPlan(
  client: CompanyCamClient,
  projectId: string,
  template: ChecklistTemplateSummary,
): Promise<ChecklistPlan> {
  const checklists = asArray(await client.get(`/projects/${encodeURIComponent(projectId)}/checklists`, { page: 1, per_page: 100 }), `/projects/${projectId}/checklists`);
  const existing = checklists.find((checklist) => stringValue(checklist.checklist_template_id) === template.id);
  if (existing) {
    return {
      action: "already-applied",
      projectId,
      template,
      checklistId: stringValue(existing.id),
      checklistName: stringValue(existing.name),
    };
  }
  return { action: "create-on-existing-project", projectId, template };
}

async function applyChecklistPlan(
  client: CompanyCamClient,
  checklistPlan: ChecklistPlan | undefined,
  fallbackProjectId: string | undefined,
  creatorEmail: string | undefined,
): Promise<unknown> {
  if (!checklistPlan || checklistPlan.action === "already-applied") {
    return checklistPlan;
  }
  const projectId = checklistPlan.action === "create-on-existing-project" || checklistPlan.action === "force-create-on-existing-project"
    ? checklistPlan.projectId
    : fallbackProjectId;
  if (!projectId) {
    throw new CliError("Cannot create checklist without a project id", EXIT_CODES.INTERNAL, { checklistPlan });
  }
  return client.post(
    `/projects/${encodeURIComponent(projectId)}/checklists`,
    { checklist_template_id: checklistPlan.template.id },
    { "X-CompanyCam-User": creatorEmail },
  );
}

function buildJobProjectName(jobNumber: string, title: string): string {
  return title.includes(jobNumber) ? title : `${jobNumber} - ${title}`;
}

function formatAddress(address: JsonObject): string {
  return [
    stringValue(address.street_address_1),
    stringValue(address.street_address_2),
    stringValue(address.city),
    stringValue(address.state),
    stringValue(address.postal_code),
    stringValue(address.country),
  ]
    .filter(Boolean)
    .join(", ");
}

function normalizeText(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function normalizeAddress(value: string): string {
  return value
    .toLowerCase()
    .replace(/\b(street|st)\b/g, "st")
    .replace(/\b(road|rd)\b/g, "rd")
    .replace(/\b(avenue|ave)\b/g, "ave")
    .replace(/\b(drive|dr)\b/g, "dr")
    .replace(/\b(lane|ln)\b/g, "ln")
    .replace(/\b(court|ct)\b/g, "ct")
    .replace(/\b(boulevard|blvd)\b/g, "blvd")
    .replace(/\b(place|pl)\b/g, "pl")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function stringOptionFromValue(value: JsonValue | undefined): string | undefined {
  const text = stringValue(value);
  return text || undefined;
}

function addOptionalString(target: JsonObject, key: string, value: string | undefined): void {
  if (value) {
    target[key] = value;
  }
}

function buildPpRow(user: Record<string, string>): Record<string, string> {
  return {
    companycam_user_id: user.id || "",
    companycam_display_name: user.display_name || "",
    companycam_email: user.email_address || "",
    companycam_phone: user.phone_number || "",
    companycam_status: user.status || "",
    companycam_role: user.user_role || "",
    companycam_user_url: user.user_url || "",
    pp_match_status: "",
    pp_name: "",
    pp_company_name: "",
    pp_service_type: "",
    pp_phone: "",
    pp_email: "",
    jobber_vendor_id: "",
    heypros_profile_url: "",
    preferred_partner_tier: "",
    default_service_area: "",
    notes: "",
  };
}

function ppReadme(activeCount: number, fullCount: number): string {
  return `# CompanyCam Preferred Partner Mapping Form\n\nGenerated from \`exports/companycam_users.csv\`.\n\n## Files\n\n- \`companycam_pp_mapping_template_active.csv\` - active CompanyCam users only (${activeCount} rows)\n- \`companycam_pp_mapping_template_full.csv\` - all exported CompanyCam users (${fullCount} rows)\n\n## Suggested Review Values\n\nUse \`pp_match_status\` as the review decision column:\n\n- \`matched\` - this CompanyCam user is a Preferred Partner and the PP identity is filled in\n- \`not_pp\` - this user is not a Preferred Partner\n- \`needs_review\` - possible PP, but identity is uncertain\n- \`duplicate\` - duplicate CompanyCam user for the same person/company\n- \`inactive_old\` - old/deleted account retained for history only\n\nFill in the PP columns where known. Leave unknown values blank instead of guessing.\n`;
}

function numberOption(parsed: ParsedArgs, key: string): number | undefined {
  const raw = parsed.options[key];
  if (raw === undefined || raw === true) {
    return undefined;
  }
  const value = Number(raw);
  if (!Number.isFinite(value)) {
    throw new CliError(`--${key} must be a number`, EXIT_CODES.VALIDATION);
  }
  return value;
}

function positiveIntOption(parsed: ParsedArgs, key: string, fallback: number): number {
  const raw = parsed.options[key];
  if (raw === undefined || raw === true) {
    return fallback;
  }
  const value = Number(raw);
  if (!Number.isInteger(value) || value < 1) {
    throw new CliError(`--${key} must be a positive integer`, EXIT_CODES.VALIDATION);
  }
  return value;
}

function requiredStringOption(parsed: ParsedArgs, key: string): string {
  const value = stringOption(parsed, key);
  if (!value) {
    throw new CliError(`--${key} is required`, EXIT_CODES.VALIDATION);
  }
  return value;
}

function stringOption(parsed: ParsedArgs, key: string): string | undefined {
  const raw = parsed.options[key];
  if (raw === undefined || raw === true) {
    return undefined;
  }
  const value = String(raw).trim();
  return value || undefined;
}

function stringValue(value: JsonValue | undefined): string {
  return typeof value === "string" || typeof value === "number" ? String(value) : "";
}

function output(parsed: ParsedArgs, payload: Record<string, unknown>): number {
  if (parsed.json) {
    console.log(JSON.stringify(payload, null, 2));
    return EXIT_CODES.OK;
  }
  printHuman(payload);
  return EXIT_CODES.OK;
}

function printHuman(payload: Record<string, unknown>): void {
  const command = String(payload.command || "companycam");
  console.log(`CompanyCam ${command}: ok`);
  for (const [key, value] of Object.entries(payload)) {
    if (key === "ok" || key === "command") {
      continue;
    }
    if (Array.isArray(value)) {
      console.log(`${key}: ${value.length} item(s)`);
      continue;
    }
    if (value && typeof value === "object") {
      console.log(`${key}: ${JSON.stringify(value)}`);
      continue;
    }
    console.log(`${key}: ${String(value)}`);
  }
}

function printVersion(): void {
  console.log(`companycam-cli v${VERSION}`);
}

function printHelp(): void {
  console.log(`CompanyCam CLI v${VERSION}\n\nUsage:\n  companycam status [--json]\n  companycam doctor [--json]\n  companycam version\n  companycam token check [--json]\n  companycam users export [--json]\n  companycam templates checklists list [--json]\n  companycam projects list [--page 1] [--per-page 25] [--json]\n  companycam projects create --name <name> [--dry-run] [--street-address-1 <line>] [--city <city>] [--state <state>] [--postal-code <zip>] [--country US] [--contact-name <name>] [--contact-email <email>] [--contact-phone <phone>] [--creator-email <email>] [--json]\n  companycam projects match (--address <address> | --street-address-1 <line>) [--city <city>] [--state <state>] [--postal-code <zip>] [--json]\n  companycam projects sync-job --job-number <number> --title <title> (--address <address> | --street-address-1 <line>) [--city <city>] [--state <state>] [--postal-code <zip>] [--checklist-template-id <id> | --checklist-template-name <name>] [--dry-run] [--creator-email <email>] [--json]\n  companycam projects get <id> [--json]\n  companycam projects photos <id> [--page 1] [--per-page 25] [--json]\n  companycam projects assigned-users <id> [--page 1] [--per-page 100] [--json]\n  companycam projects assign-user <id> --user-id <user-id> [--dry-run] [--creator-email <email>] [--json]\n  companycam projects apply-checklist <id> (--checklist-template-id <id> | --checklist-template-name <name>) [--force-new] [--dry-run] [--creator-email <email>] [--json]\n  companycam projects merge --source-project-id <id> --target-project-id <id> [--archive-empty-source] [--dry-run] [--creator-email <email>] [--json]\n  companycam checklists list [--page 1] [--per-page 25] [--completed true|false] [--json]\n  companycam pp template [--source exports/companycam_users.csv] [--json]\n\nEnvironment:\n  COMPANYCAM_ENV_PATH=/home/plife507/Projects/CompanyCam/.env\n  COMPANYCAM_API_TOKEN=...\n  COMPANYCAM_BASE_URL=https://api.companycam.com/v2\n  COMPANYCAM_TIMEOUT_MS=30000\n\nExit codes:\n  0 success\n  2 validation error\n  3 auth failure\n  4 rate limit\n  5 not found\n  6 config error\n  10 write-disabled or internal error\n\nLive CompanyCam project create/update/user assignment/checklist creation and empty-source duplicate archive require COMPANYCAM_WRITES_ENABLED=1. Use --dry-run to preview writes.\n`);
}

main()
  .then((code) => {
    process.exitCode = code;
  })
  .catch((error: unknown) => {
    const payload = errorToJson(error);
    const exitCode = error instanceof CliError ? error.exitCode : EXIT_CODES.INTERNAL;
    if (process.argv.includes("--json")) {
      console.error(JSON.stringify(payload, null, 2));
    } else {
      console.error(payload.error);
      if (payload.details) {
        console.error(JSON.stringify(payload.details));
      }
    }
    process.exitCode = exitCode;
  });
