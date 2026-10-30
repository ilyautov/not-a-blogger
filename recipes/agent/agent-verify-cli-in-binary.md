---
id: agent-verify-cli-in-binary
title: Verify CLI commands and flags in the script against the live CLI, not model memory
section: agent
lang: any
status: proven
evidence: measurement
tools: [Claude Code, strings, grep]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-10-23
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
A model writes a script about a tool and confidently names commands that don't exist or a wrong number of modes. In a video that debunks others' mistakes, your own invented command hurts trust most.

## Do
1. Check every command, flag and hotkey in the script against the installed version.
2. Slash commands and keys: check in the session (`/help`). If help is thin, search the binary strings.
3. No `name:"x"` string = no built-in `/x`, however often `/x` appears in the binary (it may be a custom-command example).

```bash
claude --version
claude --help | grep -E -- '--permission-mode|--setting-sources'   # flags
claude --help | sed -n '/--permission-mode/,/^  --/p'               # allowed values

B=$(readlink -f "$(command -v claude)")
strings "$B" | grep -oE 'name:"[a-z-]+",description:"' | sort -u | grep -E 'review|diff|agents'
strings "$B" | grep -oE '"ctrl\+[a-z]":"[a-zA-Z:]+"' | sort -u       # key map
```

## Verify
Every command in the script has a confirming line from `--help`, `/help` or the binary of the version you record on.

## Don't
- Don't rely on the `name:"` pattern across versions: the string format changes. Fall back to `/help` and official docs for that version.

## Evidence
On a long CLI video 4 model-invented commands were found: two before build (a non-existent command and "five modes" where `--permission-mode` has six values), two mid-render (`/review` and `/diff`, not among built-ins). Two lines had to be re-voiced.
Counted on one long video: 4 invented commands in the script, 2 caught before build and 2 mid-render; 2 lines re-voiced.

## Related
- [Clean agent run](agent-clean-run-setting-sources.md)
