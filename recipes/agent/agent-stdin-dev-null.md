---
id: agent-stdin-dev-null
title: Give claude -p and codex exec </dev/null inside a while-read loop
section: agent
lang: any
status: proven
evidence: measurement
tools: [Claude Code, Codex CLI, bash]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Batch processing (`while read file; do claude -p ...; done < list.txt`) handles only the first line and exits quietly. The agent CLI reads stdin and eats the rest of the list.

## Do
Cut the agent's stdin.

```bash
while read -r f; do
  claude -p "Edit script $f following BRIEF.md" </dev/null > "out/$(basename "$f")"
done < list.txt

while read -r f; do codex exec "review $f" </dev/null; done < list.txt
```

Alternative: read the list from another descriptor: `while read -r f <&3; do ...; done 3< list.txt`.

## Verify
Output count = list line count: `wc -l < list.txt` and `ls out | wc -l`.

## Don't
- Don't drop stdin when the agent needs piped input (`cat file | claude -p ...`): pass it explicitly per call and iterate the list via another descriptor.

## Evidence
Same loop over a 5-line list with a stdin-reading command: without `</dev/null` 1 of 5 lines processed, with it all 5.

## Related
- [Clean agent run](agent-clean-run-setting-sources.md)
