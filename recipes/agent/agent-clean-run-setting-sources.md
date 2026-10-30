---
id: agent-clean-run-setting-sources
title: Run a clean agent check with --setting-sources "" and --plugin-dir
section: agent
lang: any
status: hypothesis
evidence: experience
tools: [Claude Code]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-10-23
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
You record "how this skill or plugin works out of the box", but the agent picks up your personal copy of the same skill, your CLAUDE.md and settings. The screen won't match what a viewer gets.

## Do
1. Disable user, project and local settings; load the plugin explicitly from its folder.
2. `--plugin-dir` can be repeated for several plugins.
3. Don't use `--safe-mode` here: it also disables plugin skills.

```bash
claude -p --setting-sources "" --plugin-dir ./my-plugin \
  "Compute the margin from data.csv and name the loss-making product" </dev/null
```

## Verify
Ask the agent at the start of the run to list available skills: only skills from `--plugin-dir` appear.

## Don't
- Don't trust these flags across versions: check `claude --help` before recording.

## Evidence
- `--setting-sources ""` also skips the project's `CLAUDE.md`; `--setting-sources project` loads it. Checked with a secret word written only in `CLAUDE.md` (CLI 2.1.312): the model knew it with `project`, not with `""`. To test a `CLAUDE.md` rule, run with `project` in a clean folder.
- Without `--setting-sources ""` the run picked up a copy of the skill from the user skills folder instead of the plugin version. No measurement of the difference in answers.

## Related
- [Verify CLI commands in the live binary](agent-verify-cli-in-binary.md)
- [stdin in a loop](agent-stdin-dev-null.md)
