# v0.9.0 — Orchestration sync from herdrpowers, Antigravity, and fixes

Base: `8ae1c8d` (v0.8.1). Source: herdrpowers `main` at `1921c31`, one commit
ahead of its `origin/main` (`4c4ebe3`, v1.28.0). Source files were read
through Git objects; the source repository was not changed.

## Sync boundary

herdrpowers rewrote its history after the last sync: `7253d0f`, the boundary
named in the [2026-10-21 record](2026-10-21-orchestration-sync.md), no longer
exists there. Its equivalent is `bf43559` — that commit's `LICENSE` and
`skills/herdr/SKILL.md` are byte-identical to this repository's copies, and
all three transport scripts here matched it byte for byte. v0.8.1 had already
taken the GPT-6.2 model strings of `3251ebc`. This release covers
`bf43559..1921c31`.

## Imported

| Item | Source | Result and adaptation |
| --- | --- | --- |
| Composition profiles | `001c594` and follow-ups through `30af8c7`, `3df79b3` | `profile` selects a preset; a profile named in the task selects it for one run. Owner handoff with the unused/relay question, key-presence overlay, nested `{kind: {model, effort}}` targets, migration of legacy forms. Local profiles live in `.herdr-orchestration/profiles/`; shipped ones in `skills/orchestration/profiles/`, next to `roles.yaml`, so every install method carries them without extra packaging. |
| `any` slots | `6d806ad` | Profile-only `any` for the owner or a one-target role, filled by the task. |
| Shipped presets | `6d806ad`, `1921c31` | `fable`, `neon-fable`, `solo`, and their README, with paths and links adapted. `1921c31` (generalist on Gemini 4 Hydrogen) was not yet on herdrpowers' `origin/main`. |
| Role bindings under `roles:` | `3df79b3` | Direct values, `reviewers` instead of `reviewer`; legacy `agent:`/`agents:` and `reviewer` stay readable with a deprecation notice. |
| `decision-making` and `decision-maker` | `658f9f7` | New work task and role. The decision brief moved into `references/decision-maker-brief.md`, rewritten without workflow-pack material. |
| Effort verification | `1e2bcef`, `05eabfa`, `b0bf961` | `pane-model.sh`, `composer-submit.sh`, and the probe take an effort after the model. Muse footer support. |
| Agent lifecycle | `5314d65`, `b85b193`, `774a075` | `agent-lifecycle.sh` and its reference. It reads `.herdr-orchestration/config.yaml`; the environment variables became `HERDR_ORCHESTRATION_REPO_ROOT` and `HERDR_ORCHESTRATION_PANE_SCOPE`. |
| `reviewer_usage_limit` and the reset-crash guard | `4c38cd5` | The policy, and the helper's check that the agent survives `/clear` (reworked below). |
| Skill references | `afc23ae` and later | Transport detail in `references/` (composer keys, failure handling, task contract, lifecycle); orchestration detail in `references/profiles.md` and `references/routing.md`. |
| Default fallbacks | `001c594`, `33660bd`, `88ba12e`, `14be088` | Added the profile targets' entries. Kept the existing entries for the default roles, which upstream dropped although its defaults still name those targets. |
| Tests | the commits above | Node tests for the helpers, lifecycle, and profiles; effort and Muse fixture checks; the skill-size check. The existing Python tests remain and run against the new scripts. |

## Excluded

| Item | Reason |
| --- | --- |
| Workflow pack | `commands/`, the Antigravity command wrappers, `pane-driven-development`, `writing-plans`, the test-authoring, fix-round, documentation-impact, task, and final-branch gates, `mode: implementer`, `delegation.execution`, `/strict_full_cycle`, and the init workflow have no counterpart in this standalone repository. `integration-review` stays. |
| OpenCode plugin rework (`6d82a5c`) | This repository already ships its own OpenCode 2 plugin. |
| Superpowers refreshes, scanner and CI changes, changelogs, pack docs | Outside orchestration. |

## Antigravity

`.antigravity-plugin/plugin.json` is the native manifest. Antigravity loads
`skills/` by default, and this plugin ships no commands, so it needs no
`skills` path and no wrappers. `agy plugin validate .` (Antigravity CLI
1.5.12) passes with three skills and only the no-logo note, and
`agy plugin install` of the working tree under an isolated `HOME` installed
all three skills, the shipped profiles, and the scripts with their executable
bits. `tests/antigravity/plugin.test.mjs` keeps the manifest's name and
version in step with `package.json` and the other manifests.

## Beyond upstream

- **Cursor effort.** cursor-agent shows the selected model's display name: the base name, then one label per set parameter — context size, effort, `Fast`, `No Thinking` — built by its `format-param-summary` module (cursor-agent 2026.11.19); Max Mode is a separate flag. A live pane with `reasoning_effort: xhigh` showed `Grok 4.7 256K Extra High`. `pane-model.sh` now peels those labels off the end of the name — never into the requested model, and ignoring ` · MAX`, statusLine fields, and right-aligned footer labels — and needs exactly one effort among them. Upstream treated Cursor's trailing `Max` as a plan label and accepted only a synthetic `Reasoning:` field no CLI renders; those synthetic fixtures were replaced by the live capture and synthetic variants of it.
- **Effort `any`.** A target may write `effort: any`: no effort is fixed, the orchestrator chooses one per task and reports it. The helpers verify only the model for `any`.
- **Subagent fallback.** `delegation.subagent_fallback` (default `true`): a target whose pane is not open, and which no fallback replaces, runs in a fresh subagent of the orchestrator's own kind, reported with the constraints it lost. An explicit empty fallback list now rules out pane substitutes only; `subagent_fallback: false` restores the earlier outcome.
- **Liveness check.** `composer-submit.sh` compares the foreground process group instead of the first listed pid, and re-reads an ambiguous reading; only the shell holding the terminal ends a submission at once. herdrpowers' check exited `2` twice on a live Claude pane right after `/clear` (2026-11-14). The likely cause, not confirmed, is a reading taken while the reset restarted the agent's helper processes. When the shell does hold the terminal, the helper now discards its line with `ctrl+c`; upstream's `ctrl+u` came right after an `esc`, and zsh and bash read the two as one meta key, keeping the line.
- **Narrow panes.** The model/effort check before keys now follows the width step: opencode draws no model line at about 30 columns, so a narrow pane failed with exit `5` before the helper ever widened it.
- **Orchestrator behavior.** A review gate with no reviewer left holds instead of passing on the owner's own review; review briefs list the user's requirements in order; the orchestrator never ends its turn with a delegation in flight; waits stay shorter than the calling tool's timeout; herdr's agent state is never rewritten to force a submission.
- **SKILL.md size.** Both large skills now sit near 14 KB (upstream: about 19.6 KB against the 20,000-byte compaction limit). Rationale, observed-version tables, and examples moved to `references/`, each behind an explicit "read before" step. `SKILL.md` keeps the rules that cannot wait for a read: the scope filter, never `pane run`, the helper's exit codes, no re-delegation, and the pointers themselves; the task contract and failure handling were already references upstream.

## Validation

- `npm test`: 138 node tests — OpenCode plugin, pane footer reader, composer helper, lifecycle helper, profile assets, Antigravity manifest.
- `bash tests/pane-model/run.sh`, `effort.sh`, `muse.sh`, and `tests/skill-size/test-skill-size.sh` pass.
- Python: 16 composer/probe tests and 4 bootstrap tests pass.
- The new liveness, narrow-pane, Cursor, and effort `any` tests fail against the upstream scripts and pass here.
- `claude plugin validate` for the plugin and the marketplace, `agy plugin validate .`, JSON parsing, shell syntax, and relative links pass.
- An independent review ran in a fresh subagent, since no reviewer pane was open in the tab; its findings — notably the `ctrl+c` line discard and the Cursor label edge cases — were fixed before release.
- No live delegation was run. The only live input is the Cursor footer, read once from an idle pane without sending keys.
