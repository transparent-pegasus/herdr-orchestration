# orchestration

Agent skill that routes every task received directly from the user through the pane that received it (the orchestrator) inside [herdr](../herdr/). Who performs each kind of work, and where, comes from a routing table rather than from prose: the orchestrator resolves it, delegates through [`using-herdr-sibling-panes`](../using-herdr-sibling-panes/), and reports every non-default assignment it ran under.

## Files

- [`SKILL.md`](SKILL.md) — the skill: configuration resolution, delegation scope, the routing table, the complex-coding boundary, the review gates, exhaustion/fallback, and the delegation contract.
- [`roles.yaml`](roles.yaml) — shipped defaults: the role list, the `fallbacks:` map of substitutes for exhausted agents, `delegation.pane_scope`, and the `assignments:` routing table.
- [`agents/openai.yaml`](agents/openai.yaml) — interface metadata for OpenAI-compatible agent runners.

## Configuration

`roles.yaml` holds the defaults. A repository overrides any key of it in its own `.herdr-orchestration/config.yaml`, which wins key by key — that file is the place to customize, because a plugin install is read-only in practice and an update clobbers edits to `roles.yaml`. Unknown assignment names are reported; the old `plan-double-review` key is honored as `plan-review`, with the new name taking precedence if both appear.

Every delegation task (`complex-coding`, `simple-coding`, `chores`, `verification`, `plan-and-design`) carries a `role` and a `mode`. Work in `mode: orchestrator` runs inline; a review in that mode runs in a fresh subagent so it has independent context. The defaults keep Generalist work inline. The review gates (`plan-review`, `integration-review`) additionally carry `enabled`, and turning one off means that step goes unreviewed — which the final report says. `integration-review` runs only when implementation was split across multiple panes.

## Key properties

- Only applies to tasks that come directly from the user; delegated tasks are executed in place, never re-delegated.
- Delegation stays inside the orchestrator's own tab unless `delegation.pane_scope` widens it — a pane one tab over is usually another repository's, mid-session, and submission resets that session.
- Roles bind to agent types, optionally pinned as `agent@model`, rather than reserved panes. Model selection reads the CLI's footer, never switches a pane's model, and reports the selected pane and model line.
- A role bound to a list runs one delegation per entry; entries of the same type must pin distinct, non-overlapping model names and use separate panes.
- Review independence comes from a fresh reset session or, for `mode: orchestrator`, a fresh subagent. If independent review is unavailable or prohibited by the user, the report names the degradation.
- An exhausted entry (usage limit, or two failed delegations on matching panes) is replaced from the `fallbacks:` map, looking up the full entry before its bare type. Other models remain eligible; an entry with no matching in-scope pane is unavailable, not exhausted. Every fallback is named in the final report.
- Configuration is input: it is resolved once before the first delegation and never written from inside a run.

## License

[MIT](../../LICENSE).
