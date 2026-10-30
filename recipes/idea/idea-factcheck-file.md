---
id: idea-factcheck-file
title: Keep a fact-check file and a list of dropped claims for every video
section: idea
lang: any
status: proven
evidence: measurement
tools: [strings, grep]
learn: ../../learn/en/01-idea-hook-script.md
added: 2026-10-23
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
The script contains commands, CLI flags, or numbers, in speech or on screen.

## Do
1. Create `qa/factcheck.md` in the video project: every fact in speech and in frame → link to the primary source.
2. Add a section "do not say": common claims that the fact-check removed.
3. Verify commands and flags against the installed version of the tool, not model memory. For a binary with commands embedded as strings, `strings | grep` is enough.
4. Check on-screen numbers (illustrations, titles) as strictly as spoken numbers.

```bash
# does the installed CLI have this command?
strings "$(which some-cli)" | grep -c 'name:"review"'      # 0 → no such command
```

## Verify
Every number and command in the script and in frame has a line in `factcheck.md`.

## Don't
- Don't write commands or numbers from memory.
- Don't expect retention gains: this protects against devastating comments, not watch time.

## Evidence
- Limits video: the fact-check removed four common claims.
- Breakdown of someone else's tutorial: five errors in the original and four of our own (invented commands, wrong number of modes); two were found mid-render.
- Dry review of 104 frames of a long video found two invented numbers in illustrations and a title.
- Based on one team's experience.
Counts come from three videos: 4 claims removed, 5 + 4 errors found, 2 invented numbers in 104 reviewed frames.

## Related
- [Dry frame review before render](../qa/qa-dry-frame-review.md)
- [Script before build](idea-script-before-build.md)
- Example: [The agent said the tests passed](../../examples/agent-cheats-long/README.md)
- Example: [The whole course in 20 minutes (failure)](../../examples/course-retelling/README.md)
