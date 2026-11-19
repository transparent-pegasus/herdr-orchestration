# orchestration

Agent skill that routes every task received directly from the user inside [herdr](../herdr/). The active owner — the pane that received the task, or the owner a selected profile names — resolves the routing table, delegates through [`using-herdr-sibling-panes`](../using-herdr-sibling-panes/), and reports every non-default assignment it ran under. Delegated workers execute in place and never re-delegate.

## Files

- [`SKILL.md`](SKILL.md) — the skill: configuration resolution, delegation scope, the routing table, role assignments, the subagent fallback, the review gates, exhaustion/fallback, and the delegation contract.
- [`roles.yaml`](roles.yaml) — shipped defaults: the `roles:` bindings, the `fallbacks:` map, `delegation:` (`pane_scope`, `subagent_fallback`), the `assignments:` routing table, and the top-level `profile`, `allow_agent_lifecycle`, and `reviewer_usage_limit`.
- [`references/profiles.md`](references/profiles.md) — read before routing: profile selection and precedence, nested targets and migration, `any` slots and effort `any`, owner handoff, lifecycle permission, self-target execution, and fallback lookup.
- [`references/routing.md`](references/routing.md) — task classification, decision-making routing, the subagent fallback, and the coding boundary.
- [`references/decision-maker-brief.md`](references/decision-maker-brief.md) — the brief for a delegated `decision-making` pass.
- [`profiles/`](profiles/) — shipped profile templates (`fable`, `neon-fable`, `solo`) and their README.
- [`agents/openai.yaml`](agents/openai.yaml) — interface metadata for OpenAI-compatible agent runners.

## Configuration

`roles.yaml` holds the defaults. A repository overrides any key of it in its own hand-written `.herdr-orchestration/config.yaml`, which wins key by key — the plugin install is read-only in practice, and an update clobbers edits to `roles.yaml`. A selected profile then overlays only the keys it writes: its `roles:` entries replace bindings, and its `fallbacks`, `delegation`, and `assignments` maps merge per key. Lists replace, including `[]`. Configuration is resolved once and never written from inside a run.

Top-level `profile` names a file in the repository's `.herdr-orchestration/profiles/` or, failing that, the shipped [`profiles/`](profiles/); a profile named in the task selects it for that run, and the task fills its `any` slots. `allow_agent_lifecycle` is a strict boolean, false by default, separate from profiles and delegation. `reviewer_usage_limit` is `wait` or `skip`.

Every delegation task (`plan-and-design`, `decision-making`, `complex-coding`, `simple-coding`, `chores`, `verification`) carries a `role` and a `mode`; the review gates (`plan-review`, `integration-review`) also carry `enabled`. Turning a gate off means that step goes unreviewed — which the final report says. Unknown assignment names are reported; the old `plan-double-review` key is honored as `plan-review`.

## Key properties

- Only applies to tasks that come directly from the user; delegated tasks are executed in place, never re-delegated.
- Delegation stays inside the orchestrator's own tab unless `delegation.pane_scope` widens it — a pane one tab over is usually another repository's, mid-session, and a submit resets that session.
- Roles bind to agent types, not reserved panes. Targets are nested `{kind: {model, effort}}` mappings verified against the live footer before keys and after reset; effort `any` lets the owner pick the effort per task. Routing never switches an agent's settings.
- A role bound to a list runs one delegation per entry; entries of one type need distinct pinned models and separate panes. With no reviewer left at all, the gate holds rather than passing on the owner's own review.
- A selected profile's owner must match the reception pane, or the pane asks whether it stays unused or relays before an explicit handoff. Judgment calls and final synthesis follow `decision-making` (`roles.decision-maker`); reviewers advise.
- A target whose pane is not open, and that no fallback replaces, goes to a fresh subagent of the owner's own kind while `delegation.subagent_fallback` is `true`; the report names the lost constraints.
- An exhausted target is replaced from the `fallbacks:` map — the exact `kind@model` key, then the bare kind; a matched `[]` is authoritative. A usage-limited reviewer with no substitute follows `reviewer_usage_limit`.
- Lifecycle false prohibits starting, exiting, or restarting agents. True lets the owner start a missing target in an in-scope shell pane and end idle agents the task started, only through `agent-lifecycle.sh`.

## License

[MIT](../../LICENSE).
