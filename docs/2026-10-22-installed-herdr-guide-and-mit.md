# v0.8.0 — Installed herdr guidance and MIT distribution

Base: `5d256b3`. Reference: committed herdrpowers
`7253d0feec290f20765a593ea9684c90ea2dd7d1`.

## Changes

- Replace the bundled upstream Herdr guide with the thin bootstrap from that
  herdrpowers commit. It requires `HERDR_ENV=1`, loads the complete guide via
  `herdr --skill`, and stops Herdr operations if the runtime or guide is missing.
  It does not clone, download, cache, or embed the upstream guide.
- Keep the `herdr` skill name and interface metadata. Update its description,
  the other skills' entry instructions, and all READMEs to point to the installed
  guide. Routing, configuration, and composer-submission rules still apply.
- Use the exact MIT LICENSE from herdrpowers `7253d0f`, including both copyright
  lines: `Copyright (c) 2025 Jesse Vincent` and
  `Copyright (c) 2026 transparent-pegasus`, as requested.
- Set all three plugin manifests to version `0.8.0` and license `MIT`. The three
  marketplace manifests contain no license overrides or version fields; their
  existing schema and layout remain unchanged. All READMEs name MIT.
- Add a focused NOTICE for this distribution and its herdrpowers updates.
  Herdr remains a separately installed runtime, with its guide provided under
  its own terms. Do not carry notices for upstream files that are no longer
  included, or attribution for absent Superpowers skills.
- Mark the previous sync record as historical. It contains no copied upstream
  guide, README, or embedded diff. Earlier Git snapshots retain their original
  licensing; history is not rewritten by this release.

## Tracked-file audit

The initial `git ls-files -z` inventory contained 37 files. Every tracked file's
contents and origin were reviewed, including hidden manifests, helpers, tests,
and terminal fixtures. The final index contains 40 files after adding this
record, NOTICE, and the bootstrap test module. No submodules, binary payloads,
or generated guide copies are present.

| Files reviewed | Count | Origin and result |
| --- | --- | --- |
| `.claude-plugin/{plugin,marketplace}.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/{plugin,marketplace}.json`, `.agents/plugins/marketplace.json` | 6 | Project metadata. Only plugin manifests declare licenses; all are MIT. |
| `LICENSE`, `NOTICE` | 2 | LICENSE matches the committed MIT source exactly. NOTICE describes the current payload and historical licensing without reproducing the Herdr guide or its old notices. |
| `README.md`, `skills/{herdr,orchestration,using-herdr-sibling-panes}/README.md` | 4 | Project documentation. Remove bundled-guide claims and copying instructions; declare MIT. |
| `docs/2026-10-21-orchestration-sync.md`, this record | 2 | Project release records. Historical identifiers and provenance references contain no upstream excerpts. |
| `skills/{herdr,orchestration,using-herdr-sibling-panes}/SKILL.md`, their three `agents/openai.yaml` files, `skills/orchestration/roles.yaml` | 7 | The only known vendored upstream file, the former `skills/herdr/SKILL.md`, is replaced in full. The other two skills originate in this project; their later herdrpowers updates are distributed under MIT at `7253d0f`. The bootstrap is that commit's original wrapper. |
| `skills/using-herdr-sibling-panes/scripts/{composer-submit,pane-model,probe-composer}.sh` | 3 | Project/herdrpowers delegation helpers, not Herdr implementation code. The former two delegation skills existed before the guide was vendored (`d7721f0`, `213046b`); subsequent helper additions are traced to their herdrpowers commits. |
| `tests/composer-submit/{herdr_mock,test_composer_submit}.py` | 2 | Original offline tests added in `5d256b3`; no real guide contents. |
| `tests/herdr-guide/test_herdr_guide.py` | 1 | New offline test using synthetic guide text only. It executes the actual bootstrap code block with a mock binary. |
| `tests/pane-model/run.sh`, `tests/pane-model/fixtures/*.txt` | 13 | Footer-parser tests and terminal captures/derived fixtures from herdrpowers `e10b9ce`, distributed under MIT in `7253d0f`. These contain agent CLI screen data, not the Herdr guide, README, or implementation. |

Additional checks:

- Review the original vendoring commit `213046b`: it introduced the upstream
  guide and Apache LICENSE. The local README and interface metadata were
  project additions, and the orchestration/transport skills predate it.
- Compare every tracked file against the originally bundled guide at
  `213046b`, the v0.9.4 guide in herdrpowers `cf82b3b`, and that commit's upstream
  README. Check normalized word sequences as well as file hashes, prose,
  command blocks, and origin history. After replacement, no six-word or longer
  matching sequence remains, apart from standard license text checked separately.
  This comparison supplements the origin review; shared CLI identifiers alone
  are not treated as copied documentation or implementation.
- Search the entire inventory for licensing, vendoring, upstream attribution,
  guide excerpts, and embedded diffs. Remaining Apache mentions occur only in
  explicitly historical release/licensing notes. Current license declarations
  are MIT; no upstream Herdr wording or code requiring its notices remains.
- Compare herdrpowers' refs, status, tracked-diff hash, and untracked-file hashes
  before and after the work. The source repository is read-only throughout.

Result: no remaining bundled upstream Herdr text or implementation, and no
additional third-party source requiring retained Apache notices was found in
the current tracked distribution. The MIT change proceeds on that inventory.

## Validation

- 26 existing pane-model fixture checks pass.
- 14 existing offline composer/probe integration tests pass.
- Four new bootstrap tests pass: environment gating, complete guide output,
  an unsupported `--skill`, and a missing CLI. Failures stop without a fallback.
- Claude plugin and marketplace validation, JSON/YAML parsing, matching plugin
  versions/license fields, relative links, shell syntax, and whitespace checks
  pass. The source bootstrap and LICENSE match `7253d0f` byte for byte.
- No pane or subagent is launched; no guide output is saved in the repository.
  Runtime behavior is verified with mocks, without operating a live session.
