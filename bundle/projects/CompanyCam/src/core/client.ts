import { BASE_URL } from "./config.js";
import { CliError, EXIT_CODES } from "./errors.js";

export type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };
export type JsonObject = { [key: string]: JsonValue };

export class CompanyCamClient {
  readonly token: string;
  readonly baseUrl: string;
  readonly timeoutMs: number;

  constructor(token: string, baseUrl = BASE_URL, timeoutMs = 30000) {
    this.token = token;
    this.baseUrl = baseUrl;
    this.timeoutMs = timeoutMs;
  }

  async get(path: string, params?: Record<string, string | number | boolean | undefined>): Promise<JsonValue> {
    const url = new URL(`${this.baseUrl}${path}`);
    for (const [key, value] of Object.entries(params || {})) {
      if (value !== undefined) {
        url.searchParams.set(key, String(value));
      }
    }

    const response = await this.fetchWithTimeout(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${this.token}`,
        Accept: "application/json",
      },
    });
    const text = await response.text();
    const body = text ? parseJson(text) : null;

    if (!response.ok) {
      const details = { status: response.status, body };
      if (response.status === 401 || response.status === 403) {
        throw new CliError(`CompanyCam auth failed for GET ${path}`, EXIT_CODES.AUTH, details);
      }
      if (response.status === 404) {
        throw new CliError(`CompanyCam resource not found for GET ${path}`, EXIT_CODES.NOT_FOUND, details);
      }
      if (response.status === 429) {
        throw new CliError(`CompanyCam rate limit hit for GET ${path}`, EXIT_CODES.RATE_LIMIT, details);
      }
      throw new CliError(`CompanyCam GET ${path} failed with HTTP ${response.status}`, EXIT_CODES.INTERNAL, details);
    }

    return body;
  }

  async post(path: string, body: JsonObject, headers?: Record<string, string | undefined>): Promise<JsonValue> {
    return this.request("POST", path, body, headers);
  }

  async put(path: string, body: JsonObject, headers?: Record<string, string | undefined>): Promise<JsonValue> {
    return this.request("PUT", path, body, headers);
  }

  async patch(path: string, body: JsonObject, headers?: Record<string, string | undefined>): Promise<JsonValue> {
    return this.request("PATCH", path, body, headers);
  }

  private async request(
    method: "POST" | "PUT" | "PATCH",
    path: string,
    requestBody: JsonObject,
    extraHeaders?: Record<string, string | undefined>,
  ): Promise<JsonValue> {
    const url = new URL(`${this.baseUrl}${path}`);
    const headers: Record<string, string> = {
      Authorization: `Bearer ${this.token}`,
      Accept: "application/json",
      "Content-Type": "application/json",
    };
    for (const [key, value] of Object.entries(extraHeaders || {})) {
      if (value) {
        headers[key] = value;
      }
    }

    const response = await this.fetchWithTimeout(url, {
      method,
      headers,
      body: JSON.stringify(requestBody),
    });
    const responseBodyText = await response.text();
    const responseBody = responseBodyText ? parseJson(responseBodyText) : null;

    if (!response.ok) {
      const details = { status: response.status, body: responseBody };
      if (response.status === 401 || response.status === 403) {
        throw new CliError(`CompanyCam auth failed for ${method} ${path}`, EXIT_CODES.AUTH, details);
      }
      if (response.status === 404) {
        throw new CliError(`CompanyCam resource not found for ${method} ${path}`, EXIT_CODES.NOT_FOUND, details);
      }
      if (response.status === 429) {
        throw new CliError(`CompanyCam rate limit hit for ${method} ${path}`, EXIT_CODES.RATE_LIMIT, details);
      }
      if (response.status >= 400 && response.status < 500) {
        throw new CliError(`CompanyCam ${method} ${path} failed with HTTP ${response.status}`, EXIT_CODES.VALIDATION, details);
      }
      throw new CliError(`CompanyCam ${method} ${path} failed with HTTP ${response.status}`, EXIT_CODES.INTERNAL, details);
    }

    return responseBody;
  }

  private async fetchWithTimeout(url: URL, init: RequestInit): Promise<Response> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.timeoutMs);
    try {
      return await fetch(url, { ...init, signal: controller.signal });
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        throw new CliError(`CompanyCam request timed out after ${this.timeoutMs}ms`, EXIT_CODES.INTERNAL, {
          url: redactUrl(url),
          timeoutMs: this.timeoutMs,
        });
      }
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }
}

function redactUrl(url: URL): string {
  return `${url.origin}${url.pathname}`;
}

function parseJson(text: string): JsonValue {
  try {
    return JSON.parse(text) as JsonValue;
  } catch {
    return text;
  }
}

export function asArray(value: JsonValue, label: string): JsonObject[] {
  if (!Array.isArray(value)) {
    throw new CliError(`Expected ${label} response to be an array`, EXIT_CODES.INTERNAL, { type: typeof value });
  }
  return value.filter((item): item is JsonObject => Boolean(item) && typeof item === "object" && !Array.isArray(item));
}

export function pickName(record: JsonValue): string {
  if (!record || typeof record !== "object" || Array.isArray(record)) {
    return "(unknown)";
  }
  for (const key of ["name", "display_name", "company_name", "email_address", "email"]) {
    const value = record[key];
    if (typeof value === "string" && value.trim()) {
      return value;
    }
  }
  const first = typeof record.first_name === "string" ? record.first_name : "";
  const last = typeof record.last_name === "string" ? record.last_name : "";
  const full = `${first} ${last}`.trim();
  if (full) {
    return full;
  }
  return typeof record.id === "string" || typeof record.id === "number" ? String(record.id) : "(unknown)";
}
