# orchestration

Agent skill that routes every task received directly from the user through the pane that received it (the orchestrator) inside [herdr](../herdr/). Who performs each kind of work, and where, comes from a routing table rather than from prose: the orchestrator resolves it, delegates through [`using-herdr-sibling-panes`](../using-herdr-sibling-panes/), and reports every non-default assignment it ran under.

## Files

- [`SKILL.md`](SKILL.md) — the skill: configuration resolution, delegation scope, the routing table, the complex-coding boundary, double-review flow, exhaustion/fallback, and the delegation contract.
- [`roles.yaml`](roles.yaml) — shipped defaults: the role list, the `fallbacks:` map of substitutes for exhausted agents, `delegation.pane_scope`, and the `assignments:` routing table.
- [`agents/openai.yaml`](agents/openai.yaml) — interface metadata for OpenAI-compatible agent runners.

## Configuration

`roles.yaml` holds the defaults. A repository overrides any key of it in its own `.herdr-orchestration/config.yaml`, which wins key by key — that file is the place to customize, because a plugin install is read-only in practice and an update clobbers edits to `roles.yaml`.

Every delegation task (`complex-coding`, `simple-coding`, `chores`, `verification`, `plan-and-design`) carries a `role` and a `mode` (`delegate`, or `orchestrator` to keep it in the orchestrator's own pane). The `plan-double-review` gate additionally carries `enabled`, and turning it off means the plan is acted on unreviewed — which the final report says.

## Key properties

- Only applies to tasks that come directly from the user; delegated tasks are executed in place, never re-delegated.
- Delegation stays inside the orchestrator's own tab unless `delegation.pane_scope` widens it — a pane one tab over is usually another repository's, mid-session, and submission resets that session.
- Roles bind to agent types, not reserved panes — any idle in-scope pane of the right type can take any task.
- A role bound to a list of agent types runs one delegation per entry; that, not the task, is what makes a review a double review.
- Review independence comes from the reset session, not from picking a different pane or a different tool.
- An exhausted agent (usage limit, or two failed delegations on two panes) is replaced by its substitute from the `fallbacks:` map, and the fallback is named in the final report. An agent with no in-scope pane is unavailable, not exhausted.
- Configuration is input: it is resolved once before the first delegation and never written from inside a run.
