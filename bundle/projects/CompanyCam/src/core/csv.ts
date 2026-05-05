import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";

export function writeCsv(path: string, fields: string[], rows: Record<string, unknown>[]): void {
  mkdirSync(dirname(path), { recursive: true });
  const lines = [fields.map(escapeCsv).join(",")];
  for (const row of rows) {
    lines.push(fields.map((field) => escapeCsv(row[field])).join(","));
  }
  writeFileSync(path, `${lines.join("\n")}\n`, "utf-8");
}

export function readCsv(path: string): Record<string, string>[] {
  const lines = readFileSync(path, "utf-8").split(/\r?\n/).filter(Boolean);
  if (lines.length === 0) {
    return [];
  }
  const headers = parseCsvLine(lines[0]);
  return lines.slice(1).map((line) => {
    const values = parseCsvLine(line);
    const row: Record<string, string> = {};
    headers.forEach((header, index) => {
      row[header] = values[index] || "";
    });
    return row;
  });
}

function escapeCsv(value: unknown): string {
  if (value === null || value === undefined) {
    return "";
  }
  const text = String(value);
  if (!/[",\n\r]/.test(text)) {
    return text;
  }
  return `"${text.replaceAll('"', '""')}"`;
}

function parseCsvLine(line: string): string[] {
  const values: string[] = [];
  let current = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (quoted && char === '"' && line[index + 1] === '"') {
      current += '"';
      index += 1;
      continue;
    }
    if (char === '"') {
      quoted = !quoted;
      continue;
    }
    if (!quoted && char === ",") {
      values.push(current);
      current = "";
      continue;
    }
    current += char;
  }
  values.push(current);
  return values;
}
