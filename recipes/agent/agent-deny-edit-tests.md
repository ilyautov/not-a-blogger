---
id: agent-deny-edit-tests
title: Protect tests from the agent with deny Edit(./tests/**), not Write
section: agent
lang: any
status: proven
evidence: measurement
tools: [Claude Code]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-10-23
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
Told "make the test pass", the agent fixes the test, not the code. Same in an editing pipeline: quality checks (`tests/`, scene contract tests) get rewritten to fit a broken result, and green means nothing.

## Do
Deny edits to the tests folder in project settings, using `Edit(...)`: it covers all file-editing tools.

```json
// .claude/settings.json
{ "permissions": { "deny": ["Edit(./tests/**)"] } }
```

`Write(./tests/**)` does not apply to paths; the CLI prints a warning at startup that is easy to miss.

## Verify
Give the agent a task with a known failing test and compare file hashes.

```bash
shasum tests/test_math.py
claude -p "make the failing test pass" </dev/null
shasum tests/test_math.py      # same hash
```

## Don't
- Don't assume shell edits are blocked (`sed -i`, `cat >`): untested by us. The vendor's permissions page (code.claude.com/docs/en/permissions, read 28 Oct 2026) states that Edit deny rules also apply to recognised shell commands (`sed`, `tee`) and redirects; that is the vendor's claim, not our run. If Bash is allowed, treat this hole as open until you test it on your version.
- Don't skip re-checking after CLI updates: behavior may change.

## Evidence
Four `claude -p` runs (CLI 2.1.283) with "make the failing test pass", including one with `--dangerously-skip-permissions`: the test file never changed.

## Related
- [Clean agent run without your settings](agent-clean-run-setting-sources.md)
- [Agent works on copies](agent-work-on-copies.md)
- Example: [The agent said the tests passed](../../examples/agent-cheats-long/README.md)
