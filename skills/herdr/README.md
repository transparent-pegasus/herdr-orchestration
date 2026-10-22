# herdr

A thin bootstrap for the operating guide embedded in the installed herdr CLI.
The skill requires `HERDR_ENV=1`, prints the guide with `herdr --skill`, and
instructs the agent to read its complete output before operating the session.
The plugin does not bundle herdr's upstream skill, README, or implementation.

## Files

- [`SKILL.md`](SKILL.md) — the bootstrap, using the method in herdrpowers `7253d0f`.
- [`agents/openai.yaml`](agents/openai.yaml) — Codex interface metadata.

## Requirements

Install herdr separately, with support for `--skill`. Outside a herdr session,
or if the CLI cannot supply its guide, stop herdr operations and report the
missing prerequisite. Do not download a guide or substitute a repository copy.
Loading the guide needs no network access or separate skill installation.

## Relationship to the other skills

- [`orchestration`](../orchestration/) decides who performs each task.
- [`using-herdr-sibling-panes`](../using-herdr-sibling-panes/) governs delegation
  and composer submission.
- The CLI-supplied guide provides general session-operation instructions;
  the routing and transport rules above still apply.

## License

This bootstrap is distributed under the [MIT License](../../LICENSE).
The separately installed herdr runtime supplies its own guide under its own
terms. See the [release record](../../docs/2026-10-22-installed-herdr-guide-and-mit.md)
for the removal of the former bundled guide.
