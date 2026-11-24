# v0.9.1 — Owner-chosen effort for the generalist

The base is herdr-orchestration `28ef877` (v0.9.0). The source is
herdrpowers `main` at `0dfb1da` (v1.29.0).

## Sync boundary

The [2026-11-19 sync](2026-11-19-orchestration-sync.md) reviewed through
`1921c31`. This sync covers the orchestration skills, profiles, and their
tests in `1921c31..0dfb1da`. The single source commit carries back most of
the changes introduced in v0.9.0.

## Imported

| Item | Source | Result |
| --- | --- | --- |
| Generalist effort | `0dfb1da` | The `fable` and `neon-fable` profiles let the owner choose effort per task for Gemini 4 Hydrogen in Antigravity. The profile tests check both shipped settings and the `solo` owner binding. |
| Profile handoff and lifecycle guidance | `0dfb1da` | The handoff carries the resolved subagent fallback setting. The profile reference scopes lifecycle permission to Herdr agent processes. |

## Excluded

| Item | Reason |
| --- | --- |
| Subagent fallback, effort verification, Cursor footer parsing, composer fixes, and transport documentation | v0.9.0 already includes these changes. The composer and footer scripts match `0dfb1da` byte for byte. |
| Workflow commands, pack documentation, and changelog | Outside the standalone orchestration sync boundary. |

## Beyond upstream

Standalone profiles ship inside `skills/orchestration/profiles/`. Consumer
configuration still lives under `.herdr-orchestration/` and the lifecycle
helper still reads the `HERDR_ORCHESTRATION_*` variables. The adaptations
listed in the previous sync record carry forward.

## Validation

- The focused profile test failed with the old fixed effort before the presets changed.
- `npm ci` completed. Its audit reported 24 moderate findings in the existing dependencies.
- `npm test` passed all 138 tests. The pane-model, effort, Muse, and skill-size shell checks passed.
- Python passed 16 composer and probe tests and 4 Herdr guide tests.
- Both Claude validators and the Antigravity validator passed with icon or logo notices.
- All declared release versions are `0.9.1`. The local-source marketplace files resolve the plugin manifests from the repository root.
- A fresh subagent reviewed the changes and identified the missing handoff and lifecycle guidance.
- The offline checks use fixtures and require no live delegation.
