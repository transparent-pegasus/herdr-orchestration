# herdr

The official [herdr](https://github.com/herdrdev/herdr) v0.9.4 agent skill, vendored here so the orchestration skills ship with the CLI reference they build on. Teaches an agent to inspect and control the herdr session it runs inside: workspaces, tabs, panes, agents, commands, output reads, lifecycle waits, and saved-machine targeting.

## Files

- [`SKILL.md`](SKILL.md) — the skill: `HERDR_ENV` gate, CLI discovery, pane/agent primitives, ID handling, machine selection, starting and prompting agents, running ordinary commands in a pane, read sources, and the safety rules.
- [`agents/openai.yaml`](agents/openai.yaml) — Codex interface metadata.

## Relationship to the other skills

- [`orchestration`](../orchestration/) decides *who* does a task.
- [`using-herdr-sibling-panes`](../using-herdr-sibling-panes/) is the delegation transport for agent composers that `herdr agent prompt` cannot drive reliably.
- This skill is the general herdr CLI reference underneath both.

## Upstream

Vendored from `herdrdev/herdr` v0.9.4 at tag commit `7e26bad`, unmodified, via the committed herdrpowers update `cf82b3b` (2026-10-14), which is an ancestor of `7253d0f`. Licensed under Apache License 2.0; see the repository [`LICENSE`](../../LICENSE). Re-sync by copying `SKILL.md` from the upstream repository root. This repository keeps its existing bundled guide; the later herdrpowers switch to loading `herdr --skill` is excluded from this sync.
