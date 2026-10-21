# Orchestration sync from herdrpowers

This update selects orchestration changes from the committed herdrpowers
`main` / `origin/main` at `7253d0feec290f20765a593ea9684c90ea2dd7d1`.
The source working tree, including its uncommitted upstream v7.0.0 refresh,
is excluded. Source files were read through Git objects, never copied from
that working tree. No source files, commits, or refs were changed.

## Previous sync boundary

- herdr-orchestration `863c9f3` explicitly records the full sync from
  herdrpowers `d2f3906`.
- The later `6f37056` renamed `plan-double-review` to `plan-review` and added
  this repository's `integration-review` gate. The alias handling subsequently
  added in herdrpowers `e8700a6` was still missing here.
- `53c670e`, `3408b4b`, `e35f6cd`, and `fa44c2d` correspond to herdrpowers
  `7cf2764`, `5dcc1e9`, `f28ad47`, and the pane changes in `eb5d032`.
  Both shipped shell helpers at `fa44c2d` are byte-identical to `eb5d032`.
- The effective helper boundary is therefore `eb5d032`, with older gaps in
  orchestration policy and bounded waits. Both `d2f3906..7253d0f` history and
  the current files were compared, rather than assuming everything before
  `eb5d032` had been imported.

## Imported changes

| Item | Source | Result and adaptation |
| --- | --- | --- |
| Generalist routing | `b5db5f0` | Bind Generalist to `orchestrator`; simple coding, chores, and verification run inline. Only this repository's existing tasks are updated. |
| Independent reviews in orchestrator mode | `b5db5f0` | Review tasks in `mode: orchestrator` use fresh subagent contexts; inline work remains inline. Both plan and integration reviews honor their mode. If spawning is unavailable or the user prohibits delegation, report degraded independence. No panes or subagents were launched for this sync. |
| Configuration migration | `e8700a6` | Report unknown assignment names and honor `plan-double-review` as `plan-review`. Clarify that explicit new-name values win key by key when both appear. Keep `.herdr-orchestration/config.yaml` as the repository override. |
| Bounded delegation waits | `6b67560` | Reconcile report files and pane state between bounded waits, using the corrected snapshot semantics from later fixes. |
| Invocation without executable bits | pane-related hunks of `6083671` | Invoke bundled helpers through `bash` in documentation and the probe; no upstream execution skills are imported. |
| Current wait commands | `eb6e37d` | Replace `herdr wait output` with `herdr pane wait-output`, and `herdr wait agent-status` with `herdr agent wait --until`. Document snapshot-first matching, soft wraps, timeout/server-error exit `1`, syntax-error exit `2`; probe reads `recent-unwrapped`. |
| OpenCode pane operation | `1b824e1` | Reset with `ctrl+x`, then `n`; interrupt with two `esc` presses. Probe whether reset actually lost a word from the preceding conversation. Post-marker waits accept both `idle` and `done`. |
| Model-pinned role entries | `e10b9ce` | Add `agent@model` to roles, fallbacks, selection, reporting, and exhaustion accounting. Port footer reader `pane-model.sh`, the helper's checks before input and after reset, exit `5`, and probe checks 11–12. Same-type review entries must pin distinct non-overlapping model names and use separate panes; routing never switches models. Restrict the existing manual submission fallback to unpinned entries, because it omits the model checks. |
| Shipped pinned routes | `e10b9ce` | Port the four reviewer entries, the OpenCode Coder entry, and their ordered fallbacks. Retain the existing bare `cursor: [grok]` fallback for repository overrides using unpinned types. Leave the Coder description scoped to this repository's complex-coding task. |
| Footer-reader regression fixtures | `e10b9ce` | Port the 26 offline checks and captured/derived screens for six CLIs, wrapped composers, stale headers, missing status lines, and model pickers. |
| herdr v0.9.4 CLI guide | `cf82b3b`, an ancestor of `7253d0f` | Keep the existing bundled-guide layout. Copy the last committed vendored guide byte for byte (herdr v0.9.4 tag `7e26bad`) before the excluded bootstrap conversion. Update provenance in the existing concise README rather than copying upstream's README. |
| Idle/background and suspended-agent handling | `cf82b3b` | A pane holding unfinished delegated work remains unavailable even if idle/done. Confirm its composer is visible, since retained agent identity can survive suspension. Document agy/grok background work and the limitations of recovering alternate-screen history. |
| Local release metadata and verification | adaptations in this repository | Bump the three plugin manifests from `0.6.0` to `0.7.0`; update the existing READMEs. Preserve marketplace structure and version conventions. Add offline helper/probe integration checks using a mock CLI and the test process's own PTY. |

## Excluded or already present

| Item | Decision and reason |
| --- | --- |
| Source working-tree v7.0.0 refresh | Excluded in full: uncommitted and outside the requested source revision. |
| superpowers skills and upstream refreshes | Excluded: brainstorming, writing-plans, executing-plans, debugging, code-review skills, and other upstream payload changes are outside orchestration. Only the explicitly listed pane-transport hunks from mixed commits are selected. |
| Pack commands and execution framework | Excluded: `commands/`, `pane-driven-development`, its worktree/document-copy helpers, test-authoring/fix-round gates, `mode: implementer`, `delegation.execution`, and workflow-specific rules have no counterpart in this standalone repository. |
| herdrpowers configuration and placeholders | Excluded: `.herdrpowers/config.yaml`, init workflow, and `<REPORT_DIRECTORY>` resolution belong to that pack. Keep the existing optional hand-written config, key-by-key resolution, and task report-directory convention. |
| Pane scope and availability correction | Already present: the tab/workspace/session filter and in-scope-only availability rule exist in the target. Keep them, including for model-pinned entries. |
| Plan-review rename and previous pane fixes | Already present: the rename itself, composer draft protection, shell/width/zoom guards, slash-trigger rejection, file reports, failure-mode guidance, and removal of `rtk` prefixes are retained without duplicate imports. The missing compatibility alias is imported separately. |
| Removal/replacement of integration review | Excluded: keep this repository's existing `integration-review` gate and single-implementer skip. Source pack review gates do not replace it. |
| OpenCode plugin/npm distribution (`4859ba8`) | Excluded: `.opencode-plugin/`, `package.json`, command registration, and installation changes alter distribution. OpenCode pane operation is imported independently. |
| Scanner/security/catalog changes (`c44c3a4`) | Excluded: scanner workflows, catalog packaging, and changes to unrelated skills do not improve these three skills or their routing configuration. |
| CLI-loaded herdr guide (`7253d0f`) | Excluded: replacing the bundled official guide with a `herdr --skill` bootstrap changes distribution and introduces a new installed-binary requirement. The committed v0.9.4 guide update is retained in the existing form instead. |
| MIT relicensing and attribution/distribution rewrites (`7253d0f`) | Excluded: keep Apache-2.0, the existing LICENSE, manifests' license fields, and bundled-guide attribution. |
| Source release numbers, READMEs, and changelog files | Excluded as wholesale copies: use this repository's `0.x` versions, concise READMEs, manifest layouts, and this focused sync record. |

## Validation

- `bash tests/pane-model/run.sh`: all 26 fixture checks pass.
- `python3 -B -m unittest discover -s tests/composer-submit -v`: 14 offline
  integration tests cover model rejection before input, model drift after reset,
  zoom restoration, OpenCode reset/interrupt, legacy unpinned submission, unsafe
  input/status rejection, and both successful and ineffective-reset probes.
- Shell syntax, plugin/marketplace manifests, YAML structure, relative file
  links, source-object equality, and whitespace are checked before commit.
- No live probe was run: this task explicitly prohibits other panes or agents.
  Real CLI onboarding remains an environment-specific check. The verified-key
  history in the skill is imported evidence, not a claim of new live validation.
- The source status, tracked diff hash, and untracked file hashes are compared
  against their initial values after the work.
