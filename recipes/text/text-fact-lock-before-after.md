---
id: text-fact-lock-before-after
title: Diff the edited text against the source on numbers, dates and names
section: text
lang: ru
status: hypothesis
evidence: experience
tools: [humanizer-ru, ru-humanizer, MCP]
learn: ../../learn/en/02-text-humanizer.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
After any model edit of a Russian script or post. Model edits silently shift meaning: "often more important" becomes "more important", "we are executing the plan" becomes "we executed the plan", an explanation the author never gave appears. In a video this ends up voiced and on screen.

## Do
1. After every edit, compare "after" with "before" by machine (score before/after + fact lock: numbers with units, dates, names, titles).
2. Read the logical links by eye on four axes: who did what, confidence level ("may", "usually"), conditions, numbers with units.

```bash
uvx ru-humanizer after.txt --before before.txt          # CLI: score + fact lock
claude mcp add humanizer-ru -- uvx ru-humanizer mcp     # same from an agent: MCP tool compare_texts
```

Tool: [humanizer-ru](https://github.com/ilyautov/humanizer-ru) (MIT), PyPI package `ru-humanizer`.

## Verify
Fact lock reports no lost or new numbers and names. In the eye pass, no "often" became "always".

## Don't
- Don't trust the fact lock for logic: it compares extracted items, so a swapped cause and effect with the same numbers passes.

## Evidence
No own measurement of the catch rate. The meaning-shift examples come from a blind editing run (195 ratings) in the humanizer-ru eval folder.

## Related
- [Edit locally, don't rewrite](text-local-edit-not-rewrite.md)
- [Humanize before TTS](text-humanize-script-before-tts.md)

Writing in another language? Contribute a sibling recipe next to this one (lang: <code>).
