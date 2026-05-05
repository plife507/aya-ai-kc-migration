import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';

const repoRoot = resolve(import.meta.dirname, '..');
const bin = join(repoRoot, 'bin', 'companycam.js');
const emptyEnvPath = join(mkdtempSync(join(tmpdir(), 'companycam-cli-')), 'missing.env');

function run(args, extraEnv = {}) {
  return spawnSync(process.execPath, [bin, ...args], {
    cwd: repoRoot,
    encoding: 'utf8',
    env: {
      PATH: process.env.PATH,
      HOME: process.env.HOME,
      COMPANYCAM_ENV_PATH: emptyEnvPath,
      COMPANYCAM_API_TOKEN: '',
      COMPANYCAM_WRITES_ENABLED: '',
      ...extraEnv,
    },
  });
}

test('help is headless and does not require env or token', () => {
  const result = run(['--help']);
  assert.equal(result.status, 0);
  assert.match(result.stdout, /CompanyCam CLI v0\.1\.0/);
  assert.match(result.stdout, /companycam doctor/);
  assert.equal(result.stderr, '');
});

test('version is headless and does not require env or token', () => {
  const result = run(['--version']);
  assert.equal(result.status, 0);
  assert.match(result.stdout, /companycam-cli v0\.1\.0/);
  assert.equal(result.stderr, '');
});

test('doctor reports config state without calling CompanyCam', () => {
  const result = run(['doctor', '--json']);
  assert.equal(result.status, 0);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.ok, true);
  assert.equal(payload.command, 'doctor');
  assert.equal(payload.tokenConfigured, false);
  assert.equal(payload.headless, true);
  assert.equal(payload.timeoutMs, 30000);
});

test('token check fails with stable config exit code when token is absent', () => {
  const result = run(['token', 'check', '--json']);
  assert.equal(result.status, 6);
  const payload = JSON.parse(result.stderr);
  assert.equal(payload.ok, false);
  assert.equal(payload.exitCode, 6);
  assert.match(payload.error, /Missing COMPANYCAM_API_TOKEN/);
});

test('live write refuses before any network call when write gate is disabled', () => {
  const result = run(['projects', 'create', '--name', 'TEST - headless write gate', '--json']);
  assert.equal(result.status, 10);
  const payload = JSON.parse(result.stderr);
  assert.equal(payload.ok, false);
  assert.equal(payload.exitCode, 10);
  assert.match(payload.error, /Refusing live CompanyCam project create/);
  assert.equal(payload.details.payload.name, 'TEST - headless write gate');
});

test('dry-run project create works without token or network', () => {
  const result = run(['projects', 'create', '--name', 'TEST - dry run', '--dry-run', '--json']);
  assert.equal(result.status, 0);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.ok, true);
  assert.equal(payload.dryRun, true);
  assert.equal(payload.payload.name, 'TEST - dry run');
});

test('dry-run user assignment works without token or network', () => {
  const result = run(['projects', 'assign-user', '123', '--user-id', '456', '--dry-run', '--json']);
  assert.equal(result.status, 0);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.ok, true);
  assert.equal(payload.dryRun, true);
  assert.equal(payload.method, 'PUT');
  assert.equal(payload.path, '/projects/123/assigned_users/456');
});

test('live user assignment refuses before any network call when write gate is disabled', () => {
  const result = run(['projects', 'assign-user', '123', '--user-id', '456', '--json']);
  assert.equal(result.status, 10);
  const payload = JSON.parse(result.stderr);
  assert.equal(payload.ok, false);
  assert.equal(payload.exitCode, 10);
  assert.match(payload.error, /Refusing live CompanyCam user assignment/);
  assert.equal(payload.details.path, '/projects/123/assigned_users/456');
});

test('dry-run empty-source merge/archive works without token or network', () => {
  const result = run([
    'projects',
    'merge',
    '--source-project-id',
    'duplicate',
    '--target-project-id',
    'keeper',
    '--archive-empty-source',
    '--dry-run',
    '--json',
  ]);
  assert.equal(result.status, 0);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.ok, true);
  assert.equal(payload.command, 'projects merge');
  assert.equal(payload.action, 'archive-empty-source');
  assert.equal(payload.method, 'PATCH');
  assert.equal(payload.path, '/projects/duplicate/archive');
});

test('live empty-source merge/archive refuses before any network call when write gate is disabled', () => {
  const result = run([
    'projects',
    'merge',
    '--source-project-id',
    'duplicate',
    '--target-project-id',
    'keeper',
    '--archive-empty-source',
    '--json',
  ]);
  assert.equal(result.status, 10);
  const payload = JSON.parse(result.stderr);
  assert.equal(payload.ok, false);
  assert.equal(payload.exitCode, 10);
  assert.match(payload.error, /Refusing live CompanyCam empty-source merge\/archive/);
  assert.equal(payload.details.path, '/projects/duplicate/archive');
});

test('argument validation is stable for missing --env value', () => {
  const result = run(['--env', '--json']);
  assert.equal(result.status, 2);
  const payload = JSON.parse(result.stderr);
  assert.equal(payload.exitCode, 2);
  assert.match(payload.error, /--env requires a path/);
});
