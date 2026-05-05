export const EXIT_CODES = {
  OK: 0,
  VALIDATION: 2,
  AUTH: 3,
  RATE_LIMIT: 4,
  NOT_FOUND: 5,
  CONFIG: 6,
  WRITE_DISABLED: 10,
  INTERNAL: 10,
} as const;

export class CliError extends Error {
  readonly exitCode: number;
  readonly details?: unknown;

  constructor(message: string, exitCode: number = EXIT_CODES.INTERNAL, details?: unknown) {
    super(message);
    this.name = "CliError";
    this.exitCode = exitCode;
    this.details = details;
  }
}

export function errorToJson(error: unknown): Record<string, unknown> {
  if (error instanceof CliError) {
    return {
      ok: false,
      error: error.message,
      exitCode: error.exitCode,
      details: error.details,
    };
  }
  if (error instanceof Error) {
    return {
      ok: false,
      error: error.message,
      exitCode: EXIT_CODES.INTERNAL,
    };
  }
  return {
    ok: false,
    error: String(error),
    exitCode: EXIT_CODES.INTERNAL,
  };
}
