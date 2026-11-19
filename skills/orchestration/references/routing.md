# Task Routing and Coding Boundary

This reference belongs to `orchestration`. Script paths are relative to the
skill directory (the parent of `references/`), not this directory or the
target repository. Resolve them before invoking a script.

## Task routing

Before classifying or routing, read [profiles.md](profiles.md) and resolve the
active owner, the per-key profile overlay, and the separate lifecycle policy.
Freeze them for the run. Routing then names the task and reads its assignment.

1. **Name the task.** Classify the work against the task list in [SKILL.md](../SKILL.md#delegation-tasks-and-their-assignments): design work is `plan-and-design`; judgment calls — plan resolution and finding disposition, reviewer disagreement adjudication, mid-execution rulings, and final synthesis decisions — are `decision-making`; coding splits into `complex-coding` and `simple-coding` at the boundary below; lookups, moves, log gathering, and lint/format runs are `chores`; running build, test, and lint commands is `verification`. When a piece of work spans tasks, use the heavier one (`plan-and-design` > `decision-making` > `complex-coding` > `simple-coding` > `chores`).
2. **Read its assignment.** Take `role` and `mode` from the resolved `assignments:` after the profile overlay. `delegate` to a separate target uses a matching idle in-scope pane and reset-backed submission; when no worker can be found, see "Subagent fallback" below. With a selected profile, `delegate` resolved to the active owner requires a fresh in-process subagent, including empty-reviewer reviews; lack of that capability is a reported inability, never inline delegation. `orchestrator` uses the active owner: profile-selected self-review may be same-session or use an optional subagent; no-profile reviews still require a fresh subagent. Do not substitute your own judgment for the configured route.

Every worker receives the [delegation contract](../SKILL.md#delegation-contract)
and executes without re-delegation. Owner handoff uses the separate contract
in profiles.md: a mismatched reception pane asks unused versus relay even
when a matching owner exists. Lifecycle false prohibits start, exit, and
restart during handoff, fallback, and recovery; true still requires verified
operations and protects working and unrelated agents.

## Decision-making routing

Judgment calls never stay hardcoded in the orchestrator pane when `decision-making` routes them elsewhere:

- **With `mode: delegate`** (a separate target, or a profile self-target subagent), the active owner writes a self-contained, read-only decision brief per [decision-maker-brief.md](decision-maker-brief.md) naming the plan, the relevant reports and diff, and the exact disagreement, conflict, or synthesis question. It records the rulings returned in the brief's report file in the run's report before dispatching follow-up work or edits.
- **With `mode: orchestrator`**, the active owner decides directly (or via an optional subagent when a profile is selected) and records the rulings in the run's report.

The active owner retains orchestration, transport, worktrees, and mechanical integration; the `decision-maker` decides plan resolution, review finding acceptance and disagreements, execution rulings, and final synthesis. User decisions — plan approval, the reception pane's `unused` versus `relay` role, the integration option — remain with the user.

## Delegation scope

Tabs usually separate projects; a reset-backed submit in another tab can discard that project's session. Respect the configured `delegation.pane_scope` filter even when a matching agent exists outside it.

An out-of-scope pane is neither a candidate nor a fallback and does not count toward availability. When no in-scope target exists, wait, use allowed fallbacks, take the subagent fallback, or report degradation. Never widen scope mid-run. `using-herdr-sibling-panes` applies the filter — see "Delegation scope" there for the exact `herdr pane list` query.

## Subagent fallback

Applies when the resolved `delegation.subagent_fallback` is `true` and a
separate worker target — a work task's role target, or one slot of a review —
is **unavailable**: no live in-scope agent matches it (a busy match is waited
for, never replaced), lifecycle permission did not start one, and its fallback
lookup left no usable substitute. An explicit empty fallback list rules out
pane substitutes only; set `subagent_fallback: false` to rule out this step.

1. Spawn a **fresh in-process subagent of the active owner's own agent kind** — the owner's native subagent facility, such as Claude Code's agent tool for a Claude owner. It works in the same repository or worktree as the pane would have.
2. Give it the same self-contained brief a pane would get: the delegation contract, edit policy, exact scope, report file, and the no-re-delegation clause. It never starts, ends, or messages panes.
3. It carries none of the target's kind, model, or effort. The owner may choose a model its runtime offers, but never presents the subagent as the configured target.
4. **Reviews:** one subagent covers all unavailable slots of one review — subagents of one kind add a fresh context, not another model. Its fresh context makes it an independent-context review; report it as a subagent fallback, beside the slots that ran in panes.
5. **Work:** treat its result like any delegated result — a claim to verify, then integrate.

The report names, per delegation, the unavailable target, the subagent
fallback, and the lost constraints. The step does not apply to exhausted
targets (usage limits, two markerless delegations; those keep their fallback
and `reviewer_usage_limit` rules), to owner selection or handoff, or to tasks
whose resolved mode already runs at the owner. If the runtime cannot spawn a
subagent, the target stays unavailable and the usual degradation applies.

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
