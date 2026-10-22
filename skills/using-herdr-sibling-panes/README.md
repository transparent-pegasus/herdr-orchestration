# using-herdr-sibling-panes

Agent skill for delegating work from an orchestrator pane to idle sibling agent panes inside [herdr](../herdr/) — operational repo work (tests, lint, file reads, git inspection, command output) when used standalone, or any routed task when serving as the delegation transport for the [orchestration](../orchestration/) skill. Provides a race-free, composer-safe submission sequence and a task contract with unique completion markers.

## Files

- [`SKILL.md`](SKILL.md) — the skill: when to delegate, delegation scope, the composer-safe submission sequence, the task contract, and failure/exhaustion handling.
- [`scripts/composer-submit.sh`](scripts/composer-submit.sh) — bundled helper that checks the pane is a live agent at a usable width, clears the composer, resets the session, submits exactly one instruction with bounded settle points, and confirms the pane started.
- [`scripts/pane-model.sh`](scripts/pane-model.sh) — reads a pane's footer model line and optionally matches a model; also accepts captured screen text for offline checks.
- [`scripts/probe-composer.sh`](scripts/probe-composer.sh) — run once per agent CLI (and after every upgrade) to verify width, clear, reset effectiveness, submit, marker capture, interrupt, survival, and model checks.

## Key properties

- Requires `HERDR_ENV=1` and applies to whichever pane is acting as the orchestrator for the task.
- Delegation is confined to the orchestrator's own tab by default (`delegation.pane_scope`) — a cross-tab pane is usually another repository's, and submission resets its session.
- Never uses `pane run` for agent-pane prompts — agent composers need dismiss/submit key sequences with settle delays to avoid stale or concatenated input.
- Never uses `ctrl+c`: on an idle Codex composer it quits the TUI. `ctrl+u` clears the composer instead. `ctrl+enter` does not submit in Codex; `enter` does.
- Rejects instructions holding an embedded newline or a bare `/word`: the composer's slash popup opens mid-paste and corrupts the submission. Invoke the bundled scripts with `bash` so installs that strip executable bits still work.
- Refuses a pane whose agent has exited and left a shell prompt, and a pane too narrow for its composer to accept Enter — zooming it temporarily and restoring the tab's zoom on every exit path.
- OpenCode resets with `ctrl+x`, then `n`, and interrupts with two `esc` presses. The probe checks that a reset actually discarded the old conversation.
- Completion is detected by matching a unique marker with `herdr pane wait-output`, split into fragments in the prompt so the marker never matches the prompt itself. On long work, wait in bounded stretches and check the report file; `herdr agent wait --until idle --until done` accepts either settled state.
- Do not reuse panes with unfinished delegations even when they report `idle` or `done`; agy and grok can keep working in the background. Confirm a visible composer before sending input to an agent whose identity may have survived suspension.
- Delegated panes write their reports to files, because terminal scrollback is lossy, and are forbidden from `git checkout`/`restore`/`stash`/`clean`/`reset` — sibling edits may be in flight.
- A model-pinned `agent@model` entry selects only panes whose footer matches (`pane-model.sh`). The helper checks before any key and after the reset; a mismatch exits `5` without submitting the instruction.
- An entry is exhausted after a usage-limit message, or two markerless delegations on two matching panes; the orchestration skill then substitutes from its `fallbacks:` map. Helper exits `2`, `4`, and `5` never started a delegation and never count toward that.

## License

[MIT](../../LICENSE).
