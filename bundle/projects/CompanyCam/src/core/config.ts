import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { CliError, EXIT_CODES } from "./errors.js";

export const BASE_URL = "https://api.companycam.com/v2";

export interface CliConfig {
  repoRoot: string;
  envPath: string;
  baseUrl: string;
  token?: string;
  timeoutMs: number;
  writesEnabled: boolean;
}

export function repoRootFromModule(): string {
  const moduleDir = dirname(fileURLToPath(import.meta.url));
  if (moduleDir.endsWith("/src/core")) {
    return resolve(moduleDir, "../..");
  }
  if (moduleDir.endsWith("/dist/core")) {
    return resolve(moduleDir, "../..");
  }
  return resolve(moduleDir, "..");
}

export function loadDotenv(path: string): Record<string, string> {
  if (!existsSync(path)) {
    return {};
  }
  const values: Record<string, string> = {};
  for (const rawLine of readFileSync(path, "utf-8").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#") || !line.includes("=")) {
      continue;
    }
    const [rawKey, ...valueParts] = line.split("=");
    const key = rawKey.trim();
    const value = valueParts.join("=").trim().replace(/^[']|[']$/g, "").replace(/^[\"]|[\"]$/g, "");
    if (key) {
      values[key] = value;
    }
  }
  return values;
}

export function loadConfig(envOverride?: string): CliConfig {
  const repoRoot = repoRootFromModule();
  const envPath = resolve(envOverride || process.env.COMPANYCAM_ENV_PATH || resolve(repoRoot, ".env"));
  const dotenv = loadDotenv(envPath);
  const token = process.env.COMPANYCAM_API_TOKEN || dotenv.COMPANYCAM_API_TOKEN;
  const baseUrl = process.env.COMPANYCAM_BASE_URL || dotenv.COMPANYCAM_BASE_URL || BASE_URL;
  const timeoutMs = parseTimeoutMs(process.env.COMPANYCAM_TIMEOUT_MS || dotenv.COMPANYCAM_TIMEOUT_MS);
  const writesEnabled = process.env.COMPANYCAM_WRITES_ENABLED === "1";
  return { repoRoot, envPath, baseUrl, token, timeoutMs, writesEnabled };
}

export function requireToken(config: CliConfig): string {
  if (!config.token) {
    throw new CliError(
      "Missing COMPANYCAM_API_TOKEN. Set COMPANYCAM_ENV_PATH or create .env from .env.example.",
      EXIT_CODES.CONFIG,
    );
  }
  return config.token;
}

function parseTimeoutMs(raw: string | undefined): number {
  if (!raw) {
    return 30000;
  }
  const value = Number(raw);
  if (!Number.isInteger(value) || value < 1000) {
    throw new CliError("COMPANYCAM_TIMEOUT_MS must be an integer >= 1000", EXIT_CODES.CONFIG);
  }
  return value;
}
