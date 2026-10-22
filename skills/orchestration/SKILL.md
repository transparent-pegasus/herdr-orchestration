---
name: orchestration
description: "Route every task received directly from the user through the pane that received it (the orchestrator) in herdr unless the user explicitly denies orchestration. Does NOT apply to tasks delegated from another pane — execute those yourself, never re-delegate. Routing comes from the repository's .herdr-orchestration/config.yaml, falling back to the skill's roles.yaml defaults: a role list plus a role and a mode assigned to every delegation task — complex coding, simple coding, chores, verification, planning, and the plan and integration reviews. That resolved YAML is the source of truth for every route; read it rather than assuming a default. Delegation runs through using-herdr-sibling-panes, and stays inside the orchestrator's own tab unless the configuration widens the scope. Every task is reassignable and every review individually togglable; any assignment the repo changed and any disabled review is named in the final report. Roles bind to agent types and optional models — any idle matching pane can take the task, a role bound to a list runs one delegation per entry, and an exhausted entry is replaced by its substitute from the fallbacks map."
---

# Orchestration

## Configuration resolution

Two files answer "who does what, and which reviews run", in this order:

1. **`<repo-root>/.herdr-orchestration/config.yaml`** — the target repository's own configuration. Wins key by key. It is optional and hand-written; most repositories have none.
2. **[`roles.yaml`](roles.yaml)** — the skill's shipped defaults. Supplies every key the repo file omits.

Read both at the start of every orchestrated task (the repo file may be absent — that is normal, and means defaults apply throughout). They share one schema:

- **`roles:`** — the role list: each role and the agent type(s) it binds to. Any type may be pinned as `agent@model` — `cursor@Muse Spark` means a `cursor` pane whose footer shows `Muse Spark`; see "Model-pinned entries" in `using-herdr-sibling-panes`. Wherever this skill says a role's agent type, a pinned entry means that type on that model. `orchestrator` takes no model: `orchestrator@…` is a configuration error — route the role as `orchestrator` and name the error in the report.
- **`fallbacks:`** — agent → ordered substitutes, for when an agent cannot take work. Keys and substitutes may be pinned too.
- **`delegation:`** — defaults that apply to every task: `pane_scope`, which panes are eligible at all.
- **`assignments:`** — every delegation task, each with the role that performs it.

Merging is per key, not per file: a repo config that sets only `assignments.chores.role` keeps every other assignment, every role binding, and every fallback at its default.

**Report unknown `assignments:` keys.** A key that `roles.yaml` does not define is a stale name, not a silent no-op: otherwise the intended task runs on its shipped default, potentially re-enabling a review the repo disabled. Honor the old `plan-double-review` key as `plan-review` and tell the user to rename it. If both names are present, merge the old key first and let the explicit `plan-review` values win key by key.

**Customize in the repo file, never in `roles.yaml`.** Plugin installations are read-only in practice — an update clobbers local edits — and on a checked-out copy, editing `roles.yaml` makes it diff-dirty against upstream. The rest of this skill refers to roles and task names, never to tool names.

**Never write either file from inside an orchestrated run.** The configuration is input, resolved once before the first delegation. Rewriting it mid-run to route around an unavailable agent or to escape a review gate falsifies the terms the run reported under; unavailability is what `fallbacks:` and honest degradation are for.

## Delegation scope

`delegation.pane_scope` decides which panes are eligible to receive work at all, before any role or assignment is consulted. It is resolved from the merged configuration like everything else, and defaults to `tab`.

| value | eligible panes |
|---|---|
| `tab` | only panes whose `tab_id` matches the orchestrator's — the default |
| `workspace` | any pane in the orchestrator's `workspace_id`, in any tab |
| `session` | every agent pane `herdr pane list` reports |

Delegating outside the orchestrator's tab is off by default because a tab is how a herdr user separates projects: `herdr pane list` reports a per-pane `cwd`, and a pane one tab over is usually sitting in a different repository, in a session its own user is mid-task in. A reset-backed submit would discard that session.

Scope is a filter, not a preference. An out-of-scope pane is not a candidate, not a last resort, and not a fallback target — and it does not count when deciding whether an agent type is available. When no in-scope pane of the needed type exists, that type is unavailable: wait for one to free up, take a substitute from `fallbacks:`, or degrade per the rules below. Widening the scope mid-run is not one of the options; it is a configuration change, and configuration is never written from inside a run.

`using-herdr-sibling-panes` applies the filter — see "Delegation scope" there for the exact `herdr pane list` query.

## Delegation tasks and their assignments

`assignments:` is the routing table. **The resolved YAML is the source of truth for every route and every default** — read it, never recall a default from prose. The tables below name what each task covers; who performs it and where comes from the merged configuration, and the knobs are the same for all of them.

- **`role`** — which role from `roles:` performs the task.
- **`mode`** — where it runs: `delegate` (a fresh idle pane of that role) or `orchestrator` (work runs inline in the orchestrator pane; a review runs in a fresh in-process subagent, per "Reviews in `mode: orchestrator`" below).
- **`enabled`** — review tasks only. `false` removes the gate entirely. Work tasks are mandatory: to stop delegating one, set `mode: orchestrator` — never `enabled: false`.

Resolve every task the work will touch before its first delegation, not when you reach it.

**Work tasks** — these always happen; the assignment decides who and where:

| Task | Covers |
|---|---|
| `plan-and-design` | Brainstorming, design docs, implementation plans |
| `complex-coding` | Implementation over the "Complex coding boundary" below |
| `simple-coding` | Localized, pattern-following edits under that boundary |
| `chores` | Lookups, file moves, log gathering, mechanical edits, lint/format runs |
| `verification` | Running the repository's build, test, and lint commands |

**Review tasks** — optional gates:

| Task | Off means |
|---|---|
| `plan-review` | The plan is acted on unreviewed |
| `integration-review` | A multi-pane implementation is integrated unreviewed |

`integration-review` applies only when implementation was split across more than one pane; with a single implementer there is nothing to gate, and that skip is not a disabled review.

**Every assignment the repo config changed away from `roles.yaml`, every non-default `delegation:` value, and every disabled review, is named in the final report**, next to any role that fell back and any review that degraded for lack of panes. The user configured it; the report says so, every run, so nobody later mistakes an unreviewed plan for a reviewed one.

### Roles that bind to a list

A role declared with `agents:` (a list) instead of `agent:` runs **one delegation per entry**: the task goes to a separate pane for each listed entry, and you wait for all of them before acting on any. That is where a *double* review comes from — the role, not the task. A one-entry list is a deliberate single delegation; an empty list is the same as disabling the task.

Three rules bind wherever a list role is used:

- **The delegations come from different agent types, or one type on different models.** Two slots may share a type only when both are `agent@model` entries whose models differ, compared case-insensitively, with neither containing the other: `cursor@Grok 4.7` and `cursor@Muse Spark 1.3` are two reviewers, while `cursor` beside `cursor@Grok 4.7` is the same type twice. Each entry takes its own pane. A configuration or a fallback that breaks this leaves that slot unavailable; run with fewer.
- **Degrade, never block.** An entry counts as available if any in-scope pane matches its type and, when pinned, its model, even if it is busy — wait for busy panes, never interrupt them. If only one listed entry is available, run that one and state that the others were skipped. If none is available, fall back per "Exhaustion and fallback", and state what independence was lost.
- **Say which it was.** Full set, degraded set, or single — the report names it, every time.

Compare findings across the returned reviews, resolve disagreements, and only then act. Reviewers advise; the orchestrator decides.

### Reviews in `mode: orchestrator`

A review task whose resolved mode is `orchestrator` runs in a fresh in-process subagent, with the same self-contained review brief a delegated pane would receive: scope, diff or paths, repository standards, and report-file path. Its fresh context supplies the independence that a reset pane provides.

- **Never call an inline self-review independent.** If no subagent can be spawned, or the user prohibits delegation, the review has degraded; name that loss in the report.
- **Use the same brief.** It must stand alone, without the orchestrator's conversation context; the review reads the work product and its requirements.
- **Work tasks still run inline.** This exception changes only review tasks in `mode: orchestrator`.
- **Name the reviewer.** Report that the review ran in a subagent alongside the panes that ran delegated reviews.

A list role still means one review per entry. In this mode those are fresh subagents of the orchestrator's own agent type; pane-type and model selection apply only to `mode: delegate`.

### What no assignment can change

- **Review independence is the fresh session, not pane ID.** A `mode: delegate` review may use any idle pane matching the resolved role entry, including the pane that did the work, because submission resets the session. Do not apply a prefer-different-type heuristic. An unreset continuing session must not review its own work product; disabling a review removes it rather than converting one into that kind of self-review. A review in `mode: orchestrator` gets its fresh context from a subagent. If a config tries to turn a still-on review into an in-session self-review, honor the fresh-context rule, ignore that part of the config, and say so in the report.
- **Delegated reviews from a list role come from different agent types, or one type on distinct pinned models.** A config or fallback that breaks the list rules above leaves that slot unavailable.

## Role assignments

Panes are NOT reserved per role. Roles bind to agent types, not to specific panes: at delegation time, pick any idle pane of the matching agent type that is within `delegation.pane_scope`. A pane that just finished a review can take a coder or generalist task next, and vice versa. When no in-scope pane of the right type is idle, wait or run the work in the orchestrator pane — do not interrupt a working pane, and do not reach outside the scope.

For an `agent@model` entry the pane must also show that model in its footer. Routing selects such a pane; it never sends `/model` or otherwise switches a pane's model. Name the pane ID and its model line in the report for every delegation to a pinned entry.

## Orchestrator

Apply this skill only when the task came directly from the user. Whichever pane the user enters the instruction into becomes the orchestrator for that task — do not assume or require a specific tool for it. The orchestrator keeps final synthesis and user communication; delegated agents report back to it.

**No re-delegation.** If your task arrived as a delegated instruction from another pane (not from the user), this skill does not apply: execute the task yourself in your own pane and never delegate it onward, even if it looks routine. Re-delegation creates cascades where multiple panes contend for the same siblings and no one does the work.

Before inspecting or controlling the session, follow [`herdr`](../herdr/SKILL.md) to load the installed CLI's complete guide with `herdr --skill`. Stop herdr operations if its environment check or guide loading fails.

Use `using-herdr-sibling-panes` for every delegation. Submit through its bundled `composer-submit.sh` and wait for the delegated result before integrating it. Do not use `pane run` for agent-pane prompts.

## Task routing

Routing is two steps: name the delegation task, then read its assignment.

1. **Name the task.** Classify the work against the task list above: design work is `plan-and-design`; coding splits into `complex-coding` and `simple-coding` at the boundary below; lookups, moves, log gathering, and lint/format runs are `chores`; running build/test/lint commands is `verification`. When a piece of work spans tasks, use the heavier one (`plan-and-design` > `complex-coding` > `simple-coding` > `chores`).
2. **Read its assignment.** Take `role` and `mode` from `assignments:`. `mode: delegate` → any idle in-scope pane matching that role's entry. `mode: orchestrator` → work runs here; a review runs in a fresh subagent per "Reviews in `mode: orchestrator`". Do not substitute your own judgment for the configured route; a repo that sent `simple-coding` to the Coder role meant it.

Every delegation must satisfy the "Delegation contract" below.

## Complex coding boundary

This boundary decides which task name the work gets — `complex-coding` or `simple-coding` — not which role it goes to. The assignment does that.

Coding work is `complex-coding` when ANY of the following holds:

* **Cross-cutting change**: the change spans 3+ files or 2+ modules/layers whose interactions must stay consistent (e.g. API + client + schema).
* **Design freedom**: there is no single obvious implementation — data structures, interfaces, or algorithms must be chosen among meaningful alternatives.
* **Stateful / concurrent logic**: async flows, locking, streaming, retries, caching, or anything where ordering and partial-failure semantics matter.
* **Non-obvious debugging**: the root cause is unknown and must be inferred from behavior; reproducing or bisecting is part of the work.
* **Risky refactor**: behavior must be preserved while structure changes, and existing tests do not fully pin the behavior down.
* **Algorithmic or performance work**: correctness or complexity analysis is required, not just wiring code together.

Coding work is `simple-coding` when ALL of the following hold:

* The change is localized (1–2 files) and the intended edit can be stated precisely up front.
* It follows an existing pattern in the codebase (add a similar handler, field, test case, config entry).
* Failure is cheap and visible — a wrong result is caught immediately by tests, types, lint, or a quick run.

Examples: renaming a symbol, adding a CRUD endpoint that mirrors an existing one, writing tests for pinned-down behavior, bumping a dependency, fixing a lint/type error → `simple-coding`. Introducing a new subsystem, reworking the streaming pipeline, fixing a race condition, changing an interface used across modules → `complex-coding`.

Default when uncertain: `complex-coding`. With the default assignments a misrouted simple task costs little on the Coder, while a complex task misrouted to the Generalist produces subtle breakage. A repo that assigns both task names to the same role makes this distinction moot — that is a legitimate configuration.

## Plan/design review

Runs when the `plan-review` gate is enabled, under "Roles that bind to a list" above — one review per entry in the resolved role, with that section's independence, degradation, and reporting rules.

Draft the plan in the orchestrator pane, then run the reviews by their resolved mode: through `using-herdr-sibling-panes` for `delegate`, or fresh subagents for `orchestrator`. Wait for all of them, compare the findings, resolve disagreements, and only then act or report. Reviewers are reviewers, not substitutes for the orchestrator's final judgment.

Each review gets a fresh context without the drafting session's reasoning. If no independent reviewer is available, the orchestrator critically reviews its own plan and states that no independent review happened.

## Integration review

Runs when the `integration-review` gate is enabled **and** implementation was split across more than one pane — the seams between independently produced pieces are what it checks. With a single implementer the gate does not run, and that is not a disabled review.

After integrating the pieces, review the integrated result by the gate's resolved mode, the same way as the plan/design review: under "Roles that bind to a list", with fresh review contexts. If no independent reviewer is available, the orchestrator critically reviews the integration itself and says no independent review happened. Compare findings, resolve disagreements, and only then report.

## Exhaustion and fallback

An agent type is exhausted when `using-herdr-sibling-panes` reports it exhausted — its output says the usage or rate limit is reached, or two delegations to two different idle panes of that type both came back with no marker and no completed work. That skill's "Failure handling" section owns the detection; this skill owns what happens next. An `agent@model` entry is exhausted as written: exhausting `cursor@Grok 4.7` leaves `cursor@Muse Spark 1.3` usable, and the two-pane rule counts only panes matching the exhausted entry.

1. Look the exhausted or unavailable entry up in the resolved `fallbacks:` map — the entry as written first, then its bare type — and take the first substitute with a usable idle pane **within `delegation.pane_scope`**, subject to the list-role rules above.
2. Re-delegate the same self-contained instruction to the substitute. Do not rewrite the task to suit it.
3. If the agent has no `fallbacks:` entry in either file, or every substitute is itself unavailable, degrade: run the work in the orchestrator pane if it is safe to do so, otherwise stop and report.
4. Remember the exhausted entry for the rest of the task and route around it from then on; other models of the same type remain eligible.

An entry with no matching in-scope pane is **unavailable**, not exhausted — it may have idle panes one tab over, or panes of its type on other models. Use the same fallback lookup without recording exhaustion; never widen the scope or switch a pane's model to make it match.

Always state in the final report which role fell back, to which agent, and why.

## Delegation contract

Each delegated instruction must state:

1. The task and relevant context.
2. Whether edits are allowed.
3. The exact files or commands in scope.
4. The expected output and completion signal.
5. That the recipient must execute the task itself and must not re-delegate or orchestrate (e.g. "Execute this request yourself, directly. Re-delegating to other panes or orchestrating is prohibited.").

Use the sibling-pane workflow exactly, including its bundled `composer-submit.sh` helper and settle points. Do not replace it with `pane run` or raw back-to-back key calls, and do not send a redundant follow-up prompt asking a pane to run the task. An orchestrator receives the task when the delegated work finishes.
