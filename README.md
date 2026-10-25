# herdr-orchestration

Multi-pane agent orchestration for [herdr](https://herdr.dev). Every task that arrives directly from the user is routed through the pane that received it. Who performs each kind of work, and where, comes from a routing table in `roles.yaml`, which a repository overrides key by key in its own `.herdr-orchestration/config.yaml`. The defaults keep planning and routine work in the orchestrator pane and delegate complex coding and independent reviews to sibling panes selected by agent type and model.

Requires `HERDR_ENV=1` and an installed herdr CLI that supports `herdr --skill`. The CLI supplies its operating guide at runtime. Outside herdr the skills do nothing; if the guide cannot be loaded, stop herdr operations.

## Skills

- [`orchestration`](skills/orchestration/) — orchestrator rules, configuration resolution, the routing table, delegation scope, the complex-coding boundary, the plan and integration review gates, the delegation contract, and fallback resolution.
- [`using-herdr-sibling-panes`](skills/using-herdr-sibling-panes/) — the delegation transport: composer-safe submission, model checks, the completion-marker task contract, failure handling, and a probe that verifies a new agent CLI can be driven at all.
- [`herdr`](skills/herdr/) — a thin bootstrap that loads the complete operating guide from the installed CLI with `herdr --skill`. The plugin bundles no upstream herdr guide or implementation.

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

OpenCode 2 (`opencode2`):

Clone the repository and install its dependencies:

```bash
git clone https://github.com/transparent-pegasus/herdr-orchestration.git
cd herdr-orchestration
npm ci
```

Add the clone's **absolute directory path** to `plugins` in your project's
`opencode.jsonc` or `~/.config/opencode/opencode.jsonc`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugins": ["/absolute/path/to/herdr-orchestration"]
}
```

Restart OpenCode 2. The plugin registers all three skills with their original
file paths, so relative references to `roles.yaml` and the transport scripts
resolve inside the installation. Existing skills with the same ID take
precedence. This uses the [OpenCode 2 plugin API](https://opencode.ai/v2/docs/build/plugins)
(`setup` and `ctx.skill.transform`) and the plural `plugins` setting; it requires
OpenCode 2.0.32 or later.

## Layout

```
.agents/plugins/    marketplace.json                (cross-tool; Codex reads this)
.claude-plugin/     plugin.json + marketplace.json  (Claude Code)
.codex-plugin/      plugin.json with interface block (Codex)
.cursor-plugin/     plugin.json + marketplace.json  (Cursor)
.opencode-plugin/   index.mjs                       (OpenCode 2)
index.mjs                                          OpenCode 2 local-directory entrypoint
package.json + package-lock.json                   OpenCode package and dependencies
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
python3 -B -m unittest discover -s tests/herdr-guide -v
npm ci
npm test
```

The [2026-10-21 sync record](docs/2026-10-21-orchestration-sync.md) lists imported and excluded changes from herdrpowers, their sources, and validation.

The [2026-10-22 release record](docs/2026-10-22-installed-herdr-guide-and-mit.md) records the CLI-supplied guide, tracked-file audit, and MIT release.

## License

MIT. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

Herdr is an external runtime dependency and supplies its own guide at runtime.
This distribution includes no upstream herdr skill, README, or implementation.
