# herdr-orchestration

Multi-pane agent orchestration for [herdr](https://herdr.dev). Every task that arrives directly from the user is routed through the pane that received it; that pane plans and designs, sends plans for independent double review, and delegates the rest to idle sibling agent panes over a composer-safe transport. Role assignments and exhaustion fallbacks live in one swappable `roles.yaml`.

Requires `HERDR_ENV=1`. Outside herdr the skills do nothing.

## Skills

- [`orchestration`](skills/orchestration/) — orchestrator rules, task routing, the complex-coding boundary, plan double review, the delegation contract, and fallback resolution.
- [`using-herdr-sibling-panes`](skills/using-herdr-sibling-panes/) — the delegation transport: composer-safe submission, the completion-marker task contract, failure handling, and a probe that verifies a new agent CLI can be driven at all.
- [`herdr`](skills/herdr/) — the official herdr skill, vendored unmodified from [`ogulcancelik/herdr`](https://github.com/ogulcancelik/herdr): the `herdr` CLI reference the other two build on.

## Install

Claude Code:

```
/plugin marketplace add transparent-pegasus/herdr-orchestration
/plugin install herdr-orchestration@herdr-orchestration
```

Codex:

```bash
codex plugin marketplace add https://github.com/transparent-pegasus/herdr-orchestration
codex plugin add herdr-orchestration@herdr-orchestration
```

Cursor:

```bash
cursor-agent plugin marketplace add https://github.com/transparent-pegasus/herdr-orchestration
```

## Layout

```
.agents/plugins/    marketplace.json                (cross-tool; Codex reads this)
.claude-plugin/     plugin.json + marketplace.json  (Claude Code)
.codex-plugin/      plugin.json with interface block (Codex)
.cursor-plugin/     plugin.json + marketplace.json  (Cursor)
skills/<name>/SKILL.md              the skill itself
skills/<name>/agents/openai.yaml    Codex interface metadata, per skill
```

Codex resolves plugin manifests in the order `.codex-plugin/` → `.claude-plugin/` → `.cursor-plugin/`, and Cursor falls back from `.cursor-plugin/` to `.claude-plugin/`, so the manifests are kept in sync rather than deduplicated. Codex never reads `.codex-plugin/marketplace.json`, so the cross-tool `.agents/plugins/marketplace.json` is what makes it installable there.

## Before first use with a new agent CLI

Composer key bindings differ per CLI and change across releases. `ctrl+c` quits Codex from an idle composer; `ctrl+enter` does not submit there at all. Verify a pane can actually be driven before delegating to it:

```bash
skills/using-herdr-sibling-panes/scripts/probe-composer.sh "$PANE"
```

Verified 2026-07-25 against codex 0.145.0, cursor-agent 2026.07.23-e383d2b, and grok 0.2.112.

## License

Apache License 2.0, matching upstream herdr. See [`LICENSE`](LICENSE).

`skills/herdr/SKILL.md` is copyright its herdr authors and is vendored unmodified under the same license; everything else is copyright the herdr-orchestration authors.
