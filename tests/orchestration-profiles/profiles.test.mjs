import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, readdirSync, rmSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const root = fileURLToPath(new URL('../../', import.meta.url));
const skill = join(root, 'skills/orchestration');
const profiles = join(skill, 'profiles');
const names = ['fable.yaml', 'neon-fable.yaml', 'solo.yaml'];
const read = (...path) => readFileSync(join(...path), 'utf8');
const contract = () => read(skill, 'references/profiles.md');

test('the named profile templates ship inside the orchestration skill', () => {
  assert.deepEqual(readdirSync(profiles).filter((name) => name.endsWith('.yaml')).sort(), names);
  for (const name of names) assert.ok(statSync(join(profiles, name)).isFile(), `${name} must be a file`);
});

test('every shipped profile orders owner, then roles from planning through decision-maker to generalist, then overrides', () => {
  for (const name of names) {
    const source = read(profiles, name);
    const keys = [...source.matchAll(/^([a-z-]+):/gm)].map((match) => match[1]);
    const first = keys.includes('orchestrator') ? ['orchestrator', 'roles'] : ['roles'];
    assert.deepEqual(keys.slice(0, first.length), first, name);
    assert.ok(keys.slice(first.length).every((key) => ['fallbacks', 'delegation', 'assignments'].includes(key)), name);
    const block = source.slice(source.indexOf('roles:\n')).split(/\n(?=[a-z])/)[0];
    const roles = [...block.matchAll(/^  ([a-z-]+):/gm)].map((match) => match[1]);
    assert.deepEqual([roles[0], roles[1], roles.at(-1)], ['planning-design', 'decision-maker', 'generalist'], name);
  }
});

test('fable and neon-fable give generalist work to Gemini 4 Hydrogen at an owner-chosen effort while solo keeps it with the owner', () => {
  for (const name of ['fable.yaml', 'neon-fable.yaml']) {
    assert.match(read(profiles, name), /^  generalist:\n    agy:\n      model: Gemini 4 Hydrogen\n      effort: any$/m, name);
  }
  assert.match(read(profiles, 'solo.yaml'), /^  generalist: orchestrator$/m);
});

test('neon-fable delegates planning and decisions to Fable while the task names its coder', () => {
  const source = read(profiles, 'neon-fable.yaml');
  for (const role of ['planning-design', 'decision-maker']) {
    assert.match(source, new RegExp(`^  ${role}:\\n    claude:\\n      model: Fable 5.2\\n      effort: max$`, 'm'), role);
  }
  assert.match(source, /^  coder: any$/m);
  assert.ok(source.endsWith('assignments:\n  plan-and-design:\n    mode: delegate\n  decision-making:\n    mode: delegate\n'));
});

test('solo binds every role to the owner, and the contract allows it', () => {
  const source = read(profiles, 'solo.yaml');
  assert.match(source, /^orchestrator: any$/m);
  assert.match(source, /^  coder: orchestrator$/m);
  assert.match(source, /^  reviewers: \[orchestrator\]$/m);
  for (const key of ['planning-design', 'decision-maker', 'generalist', 'coder']) {
    assert.match(contract(), new RegExp(`\\| \`roles.${key}\` \\|[^\\n]*bare \`orchestrator\`, null, \`\\[\\]\`, or literal \`none\` binds it to the active owner`));
  }
  assert.match(contract(), /\| `roles.reviewers` \|[^\n]*`\[orchestrator\]`, `\[\]`, null, or literal `none` binds it to the active owner/);
});

// Bare `any` slots are filled per run; in a list they would break slot independence.
test('profiles write any only for the owner or a single-target role', () => {
  for (const name of names) {
    for (const [line] of read(profiles, name).matchAll(/^.*\bany\b.*$/gm)) {
      if (/^ +effort: any$/.test(line)) continue;
      assert.match(line, /^(orchestrator|  (planning-design|decision-maker|coder|generalist)): any$/, `${name}: ${line}`);
    }
  }
  for (const key of ['orchestrator', 'roles.planning-design', 'roles.decision-maker', 'roles.coder', 'roles.generalist']) {
    assert.match(contract(), new RegExp(`^\\| \`${key}\` \\|[^\\n]*\\| One nested target or \`any\` `, 'm'), key);
  }
  assert.doesNotMatch(contract().match(/^\| `roles.reviewers` \|.*$/m)[0], /`any`/);
  for (const example of ['`solo Opus 5.5 max`', '`neon-fable coder: codex`']) assert.ok(contract().includes(example), example);
});

test('effort any leaves the effort to the owner and still verifies the model', () => {
  assert.match(contract(), /Effort\n`any` \(any case\) fixes no effort: the active owner picks it/);
  assert.match(read(skill, 'SKILL.md'), /effort `any` leaves the effort to the active owner/);
});

test('local profiles live in the repository config directory, shipped ones in the skill', () => {
  assert.match(contract(), /`<repo-root>\/\.herdr-orchestration\/profiles\/<name>\.yaml`/);
  assert.match(contract(), /`<skill>\/profiles\/<name>\.yaml`/);
  assert.doesNotMatch(contract(), /herdrpowers|commands\/init\.md|implementer|strict_full_cycle/);
});

test('shipped roles use direct values under roles with a comment per key', () => {
  const source = read(skill, 'roles.yaml');
  const block = source.slice(source.indexOf('\nroles:\n'), source.indexOf('\nfallbacks:'));
  const keys = [...block.matchAll(/^  ([a-z-]+):(.*)$/gm)];
  assert.deepEqual(keys.map((match) => match[1]), ['planning-design', 'decision-maker', 'reviewers', 'coder', 'generalist']);
  for (const [, key, rest] of keys) assert.match(rest, / # \S/, key);
  assert.doesNotMatch(block, /^\s+(agent|agents|description):/m);
  const assignments = source.slice(source.indexOf('\nassignments:\n'));
  assert.match(assignments, /\n  decision-making:\n[\s\S]*?\n    role: decision-maker\n    mode: orchestrator\b/);
  assert.deepEqual([...assignments.matchAll(/^  ([a-z-]+):$/gm)].map((match) => match[1]), [
    'plan-and-design', 'decision-making', 'complex-coding', 'simple-coding', 'chores', 'verification',
    'plan-review', 'integration-review',
  ]);
});

test('an unavailable target falls back to a subagent of the owner kind by default', () => {
  const source = read(skill, 'roles.yaml');
  const delegation = source.slice(source.indexOf('\ndelegation:\n'), source.indexOf('\nassignments:'));
  assert.match(delegation, /^  subagent_fallback: true$/m);
  assert.match(read(skill, 'references/routing.md'), /^## Subagent fallback$/m);
  assert.match(read(skill, 'SKILL.md'), /^## Unavailable targets and the subagent fallback$/m);
});

test('the routing table and its contract name decision-making', () => {
  assert.match(read(skill, 'SKILL.md'), /^\| `decision-making` \|/m);
  assert.match(read(skill, 'SKILL.md'), /Reviewers advise;\nthe `decision-maker` decides\./);
  assert.match(contract(), /\| `roles.<custom>` \|/);
  assert.match(contract(), /any other top-level key is an error/);
});

test('npm distribution includes the profile templates and their README', () => {
  const cache = mkdtempSync(join(tmpdir(), 'herdr-profile-pack-'));
  try {
    const result = spawnSync('npm', ['pack', '--dry-run', '--json', '--ignore-scripts'], {
      cwd: root,
      encoding: 'utf8',
      timeout: 30000,
      env: { ...process.env, npm_config_cache: cache, npm_config_offline: 'true', npm_config_update_notifier: 'false' },
    });
    assert.ifError(result.error);
    assert.equal(result.status, 0, result.stderr);
    const [pack] = JSON.parse(result.stdout);
    const shipped = pack.files.map((file) => file.path).filter((path) => path.startsWith('skills/orchestration/profiles/')).sort();
    assert.deepEqual(shipped, ['README.md', ...names].map((name) => `skills/orchestration/profiles/${name}`));
  } finally {
    rmSync(cache, { recursive: true, force: true });
  }
});
