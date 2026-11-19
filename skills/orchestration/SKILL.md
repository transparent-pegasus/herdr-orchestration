---
name: orchestration
description: "Use when handling a task received directly from the user in herdr (HERDR_ENV=1), unless the user explicitly declines orchestration — including repositories with a .herdr-orchestration/config.yaml, a composition profile, model/effort constraints, or custom role assignments. Does NOT apply to tasks delegated from another pane: execute those yourself, never re-delegate. Routing comes from the resolved YAML (repo config over the skill's roles.yaml, then the selected profile): every task — planning, decision-making, complex and simple coding, chores, verification, and the plan and integration reviews — has a role and a mode there, read rather than assumed."
---

# Orchestration

## Configuration resolution

**Before resolving ownership, classifying work, or routing any task, read
[references/profiles.md](references/profiles.md).** It owns profile selection,
key-presence precedence, target validation and migration, owner handoff,
lifecycle permission, `any` slots and efforts, and the profile-scoped
self-target routes. Resolve once and freeze the run's settings.

The base configuration answers "who does what, and which reviews run":

1. **`<repo-root>/.herdr-orchestration/config.yaml`** — the target repository's own configuration, hand-written and optional. Wins key by key.
2. **[`roles.yaml`](roles.yaml)** — the skill's shipped defaults. Supplies every key the repo file omits.

Read both at the start of every orchestrated task, then overlay only the keys
present in the selected profile. The files share this schema:

- **`roles:`** — each role key's binding: one target, `orchestrator`, or a list. Custom keys add roles. New targets use `{kind: {model: <string>, effort: <string>}}`; settings are optional, effort requires model, and effort `any` leaves the effort to the active owner. The bare `orchestrator` alias resolves to the active owner. Legacy bare kinds, `agent:`/`agents:`/`description:` sub-keys, the old `reviewer` key, and non-fallback `kind@model` remain readable, with a deprecation notice for all but bare kinds.
- **`fallbacks:`** — agent → ordered substitutes, for when an agent cannot take work. Keys and substitutes may be pinned (`kind@model`).
- **`delegation:`** — `pane_scope` (which panes are eligible at all) and `subagent_fallback` (whether an unavailable target's work goes to a fresh subagent of the owner's own kind).
- **`assignments:`** — every delegation task, each with the role that performs it.
- **`profile`** — optional preset name; its present composition and routing entries override the base configuration. The task fills its `any` slots.
- **`allow_agent_lifecycle`** — top-level strict boolean, false by default. False starts and ends no agent. True lets the active owner start a resolved target that has no live match and end idle agents the task started, only through `agent-lifecycle.sh`, which enforces the value.
- **`reviewer_usage_limit`** — top-level `wait` or `skip`, config-only: how a review gate treats a usage-limited reviewer with no substitute.

Merging is per key, not per file. Lists replace rather than concatenate.
Report assignment keys `roles.yaml` does not define: otherwise their intended
task silently runs on a default and can revive a disabled review. Honor the
legacy `plan-double-review` as `plan-review` and ask the user to rename it; if
both appear, the explicit `plan-review` values win key by key.

Customize in the repo file, never in `roles.yaml` — a plugin update clobbers
it. Configuration and the selected profile are frozen inputs during a run:
never rewrite them to escape an unavailable agent or a review gate; use the
fallbacks and report the degradation instead.

## Delegation scope

`delegation.pane_scope` filters eligible panes before any role or owner
handoff recipient is chosen. Read the resolved value and freeze it.

| value | eligible panes |
|---|---|
| `tab` | only panes whose `tab_id` matches the orchestrator's — the default |
| `workspace` | any pane in the orchestrator's `workspace_id`, in any tab |
| `session` | every agent pane `herdr pane list` reports |

An out-of-scope pane is never a candidate, a fallback, or counted toward
availability, and scope is never widened mid-run. Read
[references/routing.md](references/routing.md#delegation-scope) for the
rationale; `using-herdr-sibling-panes` holds the exact query.

## Delegation tasks and their assignments

`assignments:` is the routing table. **The resolved YAML is the source of
truth for every route and every default** — read it, never recall a default
from prose. Every task takes the same knobs:

- **`role`** — which role from `roles:` performs the task.
- **`mode`** — `delegate` uses a fresh reset-backed worker of that role; with a selected profile, a target resolving to the owner needs a fresh in-process subagent instead. `orchestrator` uses the active owner: work runs inline; a review runs per "Reviews in `mode: orchestrator`" below.
- **`enabled`** — review tasks only. `false` removes the gate entirely. Work tasks are mandatory: to stop delegating one, set `mode: orchestrator`.

Resolve every task the work will touch before its first delegation.

**Work tasks** — these always happen; the assignment decides who and where:

| Task | Covers |
|---|---|
| `plan-and-design` | Brainstorming, design docs, implementation plans |
| `decision-making` | Plan resolution, review finding acceptance and disagreements, mid-execution rulings, final synthesis decisions |
| `complex-coding` | Implementation over the coding boundary |
| `simple-coding` | Localized, pattern-following edits under that boundary |
| `chores` | Lookups, file moves, log gathering, mechanical edits, lint/format runs |
| `verification` | Running the repository's build, test, and lint commands |

**Review tasks** — optional gates:

| Task | Off means |
|---|---|
| `plan-review` | The plan is acted on unreviewed |
| `integration-review` | A multi-pane implementation is integrated unreviewed |

`integration-review` applies only when implementation was split across more
than one pane; with a single implementer there is nothing to gate, and that
skip is not a disabled review.

**The final report names every assignment the repo config or profile changed
away from `roles.yaml`, every non-default `delegation:` value, and every
disabled review**, next to any role that fell back, any subagent fallback, and
any review that degraded — so nobody mistakes an unreviewed plan for a
reviewed one.

### Roles that bind to a list

A role bound to a list runs **one delegation per entry**, and you wait for all
before acting. A one-entry list is a deliberate single delegation. A config
empty list disables the task unless a profile overrides the binding; profile
`reviewers: [orchestrator]`/`[]`/null/`none` instead selects the active owner.

- **Separate targets use different agent types, or one type on distinct pinned models.** Compare models case-insensitively, neither containing the other; a bare kind beside that kind on a model is the same type twice, and effort alone does not make a second slot. Each slot takes its own pane; leave a duplicated slot unavailable and report it.
- **Degrade, never block — until nothing is left.** A target counts as available if an in-scope live agent matches its kind and any model and effort — a wrong model does not count — even if busy: wait for it, never interrupt it. Run the available slots and report the missing ones. With nothing left to run, the review gate holds: integrate nothing that depends on it, report, and resume when a reviewer returns. The owner's own unspawned review never stands in for a gate.
- **Say which it was.** Full set, degraded set, subagent fallback, or single — the report names it, every time.

Compare findings across the returned reviews, route acceptance and
disagreements through `decision-making`, and only then act. Reviewers advise;
the `decision-maker` decides.

### Reviews in `mode: orchestrator`

**With a selected profile**, a review in `mode: orchestrator` may run in the
active owner's session, or in an optional fresh subagent at its judgment; name
same-session self-review as self-review. `mode: delegate` resolved to the
owner still mandates a fresh subagent.

**Without a profile**, a review in `mode: orchestrator` runs in a fresh
in-process subagent with the same self-contained brief a reset pane would get.
If no subagent can be spawned, the review degrades — never call an inline
self-review independent. A list role spawns one subagent per entry; the
distinct-types rule does not apply to these owner subagents.

### What no assignment can change

- **Separate review independence comes from the reset session, not the pane ID.** Any idle matching pane may review after reset, including the one that did the work; do not prefer a different type. A continuing session never grades its own work as a gate, except the profile owner-session modes above.
- **Disabling a gate removes it**; it never turns into self-review, and an empty profile composition never disables it.

## Role assignments

Panes are not reserved per role: pick any idle matching target within scope,
whatever it did last. Apply lifecycle permission before any start or exit:
false starts nothing; true starts a target that has no live in-scope match
before any fallback, and ends the task-started agents when the run is done.

Requested model and effort must match live footer evidence before any key and
after reset, per `using-herdr-sibling-panes`. With effort `any`, the active
owner picks the effort for each delegation — among matching panes, or as a
launch argument it starts under lifecycle permission — and reports what it
chose. Routing never switches an existing agent's settings. Name the pane ID
and verified footer for every constrained target.

## Unavailable targets and the subagent fallback

A target with no in-scope live match is **unavailable**, not exhausted. Wait
for a busy match; start one when lifecycle permission is true; then try its
fallbacks. When none of that yields a worker and the resolved
`delegation.subagent_fallback` is `true`, run the delegation in a **fresh
in-process subagent of the active owner's own agent kind**, with the same
self-contained brief and the no-re-delegation clause. Read
[references/routing.md](references/routing.md#subagent-fallback) before the
first one. The subagent carries none of the target's kind, model, or effort:
report it as a subagent fallback with those lost constraints. `false`, or a
runtime that cannot spawn subagents, keeps the degradation below.

## Orchestrator

Apply this skill only to direct user tasks. Without a profile the reception
pane is the owner. With a profile, follow the profiles reference: a
mismatched reception pane always asks unused versus relay before handoff or
startup, and the verified selected owner receives explicit authority and
frozen settings. The active owner keeps orchestration, coordination, and user
communication; judgment calls follow `decision-making`.

**No re-delegation.** If your task arrived as a delegated instruction from
another pane (not from the user), this skill does not apply: execute it
yourself and never delegate it onward. Re-delegation creates cascades where
panes contend for the same siblings and no one does the work.

Before inspecting or controlling the session, follow
[`herdr`](../herdr/SKILL.md) to load the installed CLI's guide with
`herdr --skill`; stop herdr operations if that fails. Use
`using-herdr-sibling-panes` and its `composer-submit.sh` for separate targets,
and wait for the result before integrating. Never use `pane run` for agent
prompts.

## Task routing

Read [references/routing.md](references/routing.md) before classifying work.
Name the delegation task, then read its resolved assignment. The
[coding boundary](references/routing.md#complex-coding-boundary) decides
between `complex-coding` and `simple-coding`; the assignment decides who.

## Plan/design review

Runs when `plan-review` is enabled, under "Roles that bind to a list". Draft
where `plan-and-design` resolves, route each review by its resolved mode,
wait for all, compare findings, and route resolution through
`decision-making`. Each review gets a fresh context without the drafting
session's reasoning.

## Integration review

Runs when `integration-review` is enabled **and** implementation was split
across more than one pane: the seams between independently produced pieces
are what it checks. Review the integrated result the same way as a plan
review, then route the findings through `decision-making`.

## Exhaustion and fallback

A target is exhausted when `using-herdr-sibling-panes` reports a usage limit,
or two delegations to different idle panes of that target return no marker
and no completed work. Exhausting one pinned model leaves the others usable.

1. Look the target up in the resolved `fallbacks:`: a nested target becomes `kind@model`; bare kind only when that exact key is absent; a matched `[]` is authoritative. Take the first usable in-scope substitute, subject to the list rules. Substitutes have no effort constraint; discard the primary effort.
2. Re-delegate the same self-contained instruction to the substitute; do not rewrite the task to suit it.
3. A usage-limited reviewer with no substitute follows `reviewer_usage_limit`: `wait` holds the gate until the limit resets; `skip` passes on the remaining reviewers and holds only when none is left. Neither lets the owner's own review stand in.
4. Otherwise report the degradation: without a profile, safe work may run in the owner; with a profile, a task resolving to the owner obeys its mode, and an impossible mandatory subagent is reported as inability.
5. Remember the exhausted target, with its pinned model, for the rest of the task.

Report which role fell back, to which target, why, and which constraints were
lost. Fallback alone never authorizes startup.

## Delegation contract

Each delegated instruction — to a pane or a subagent — must state:

1. The task and relevant context.
2. Whether edits are allowed.
3. The exact files or commands in scope.
4. The expected output and completion signal.
5. That the recipient executes the task itself and must not re-delegate or orchestrate ("Execute this request yourself, directly. Re-delegating to other panes or orchestrating is prohibited.").

A review brief also lists the user's requirements for this task verbatim, in
the order they were given, and asks for a verdict on each — met, partial,
unmet, or superseded by a later requirement — with file and line evidence. A
later requirement wins where two conflict; code findings come after.

Use the sibling-pane helper and its settle points for separate targets; never
replace it with `pane run` or raw keys, and never send a redundant follow-up
prompt. Owner handoff is a separate transfer contract in the profiles
reference, not a worker delegation.
