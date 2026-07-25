# pegasus-skills

Agent skills, packaged once and installable in Claude Code, Codex and Cursor. Skills are addressed as `pegasus-skills:<name>`.

The current set covers [herdr](https://herdr.dev) multi-pane orchestration. More, unrelated skills will land here — the namespace is deliberately general, so nothing outside `skills/<name>/` assumes a topic.

## Skills

### herdr

Both require `HERDR_ENV=1` and do nothing outside herdr.

- [`orchestration`](skills/orchestration/) — routes every task that arrives directly from the user through the pane that received it: that pane plans and designs, sends plans for independent double review, delegates complex coding and routine work to sibling panes, and substitutes a fallback agent when one is exhausted. Assignments live in [`roles.yaml`](skills/orchestration/roles.yaml).
- [`using-herdr-sibling-panes`](skills/using-herdr-sibling-panes/) — the delegation transport: composer-safe submission, the completion-marker task contract, failure handling, and a probe that verifies a new agent CLI can be driven at all.

## Install

Claude Code:

```
/plugin marketplace add transparent-pegasus/pegasus-skills
/plugin install pegasus-skills@pegasus-skills
```

Codex:

```bash
codex plugin marketplace add https://github.com/transparent-pegasus/pegasus-skills
codex plugin add pegasus-skills@pegasus-skills
```

Cursor:

```bash
cursor-agent plugin marketplace add https://github.com/transparent-pegasus/pegasus-skills
```

Working on the skills themselves? Point the marketplace at the checkout instead of the URL — `codex plugin marketplace add /path/to/pegasus-skills` — and the plugin resolves from `./` in place.

## Layout

```
.agents/plugins/marketplace.json    cross-tool marketplace (Codex reads this one)
.claude-plugin/                     plugin.json + marketplace.json  (Claude Code)
.codex-plugin/plugin.json           Codex manifest, with the interface block
.cursor-plugin/                     plugin.json + marketplace.json  (Cursor)
skills/<name>/SKILL.md              the skill itself
skills/<name>/agents/openai.yaml    Codex interface metadata, per skill
```

Manifests are written out per tool rather than shared, because each CLI resolves a different, only partly overlapping set of paths:

- **Plugin manifest** — Codex tries `.codex-plugin/plugin.json`, then `.claude-plugin/plugin.json`, then `.cursor-plugin/plugin.json`.
- **Marketplace manifest** — Codex tries `.agents/plugins/marketplace.json`, `.agents/plugins/api_marketplace.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/marketplace.json`. It does **not** read `.codex-plugin/marketplace.json`, which is why the cross-tool `.agents/` path is the one that makes Codex installable. Cursor reads `.cursor-plugin/marketplace.json` and falls back to `.claude-plugin/marketplace.json`.

Adding a skill means one new `skills/<name>/` directory; no manifest changes, because every tool is pointed at `./skills/`.

## Before first use with a new agent CLI

Composer key bindings differ per CLI and change across releases. `ctrl+c` quits Codex from an idle composer; `ctrl+enter` does not submit there at all. Verify a pane can actually be driven before delegating to it:

```bash
skills/using-herdr-sibling-panes/scripts/probe-composer.sh "$PANE"
```

Verified 2026-07-25 against codex 0.145.0, cursor-agent 2026.07.23-e383d2b, and grok 0.2.112.
