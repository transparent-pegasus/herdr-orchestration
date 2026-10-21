# herdr-orchestration

Multi-pane agent orchestration for [herdr](https://herdr.dev). Every task that arrives directly from the user is routed through the pane that received it. Who performs each kind of work, and where, comes from a routing table in `roles.yaml`, which a repository overrides key by key in its own `.herdr-orchestration/config.yaml`. The defaults keep planning and routine work in the orchestrator pane and delegate complex coding and independent reviews to sibling panes selected by agent type and model.

Requires `HERDR_ENV=1`. Outside herdr the skills do nothing.

## Skills

- [`orchestration`](skills/orchestration/) — orchestrator rules, configuration resolution, the routing table, delegation scope, the complex-coding boundary, the plan and integration review gates, the delegation contract, and fallback resolution.
- [`using-herdr-sibling-panes`](skills/using-herdr-sibling-panes/) — the delegation transport: composer-safe submission, model checks, the completion-marker task contract, failure handling, and a probe that verifies a new agent CLI can be driven at all.
- [`herdr`](skills/herdr/) — the official herdr v0.9.4 skill, vendored unmodified from [`herdrdev/herdr`](https://github.com/herdrdev/herdr): the `herdr` CLI reference the other two build on.

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
bash skills/using-herdr-sibling-panes/scripts/probe-composer.sh "$PANE"
# For a model-pinned role entry, also pass the model:
bash skills/using-herdr-sibling-panes/scripts/probe-composer.sh "$PANE" "GPT-6.1 Sol"
```

The imported checks were verified in herdrpowers on 2026-10-09 against herdr 0.9.3, including OpenCode 1.18.35. See the transport skill for the per-CLI results and the Grok status-detection limitation. This repository's offline checks do not operate live panes:

```bash
bash tests/pane-model/run.sh
python3 -B -m unittest discover -s tests/composer-submit -v
```

The [2026-10-21 sync record](docs/2026-10-21-orchestration-sync.md) lists imported and excluded changes from herdrpowers, their sources, and validation.

## License

Apache License 2.0, matching upstream herdr. See [`LICENSE`](LICENSE).

`skills/herdr/SKILL.md` is copyright its herdr authors and is vendored unmodified under the same license; everything else is copyright the herdr-orchestration authors.
