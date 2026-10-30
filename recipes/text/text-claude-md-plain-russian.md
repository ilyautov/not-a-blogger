---
id: text-claude-md-plain-russian
title: Put a measurable plain-language rule for Russian into CLAUDE.md and measure it before and after
section: text
lang: ru
status: hypothesis
evidence: measurement
tools: [Claude Code, humanizer scanner]
learn: ../../learn/en/02-text-humanizer.md
added: 2026-10-28
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
The agent answers in Russian with long intros, summaries, chained clauses and em dashes. Simplified Technical English rules don't transfer to Russian, and "write simply" in a prompt changes nothing measurable.

## Do
1. Put one rule into the project's `CLAUDE.md`, with countable parts:

```text
Пиши простым русским: сначала ответ, одна мысль в предложении, до 15 слов, без вступлений, выводов и длинных тире.
```
("Write plain Russian: answer first, one thought per sentence, up to 15 words, no intros, no conclusions, no em dashes.")

2. Measure before and after on the same questions, in a clean folder, with only project settings loaded and no tools:

```bash
cd "$(mktemp -d)" && cp /path/to/CLAUDE.md . 
claude -p --setting-sources project --tools "" --no-session-persistence "$QUESTION" </dev/null > after-1.txt
```

3. Count per answer: words, longest sentence in words, em dashes, scanner markers and score (any Russian AI-text scanner). Compare medians, not single answers.
4. Use `--setting-sources project`, not `""`: with an empty list `CLAUDE.md` is not read at all, and you measure the bare model twice.

## Verify
After the rule: fewer words, longest sentence ≤ ~16 words, fewer scanner markers; the answers still answer the question (read three of them).

## Don't
- Don't expect the rule to remove em dashes completely: it halved them, not zeroed them.
- Don't call the rule proven from one run per question: rerun with more questions and runs first.

## Evidence
8 general questions × 1 run each (CLI 2.1.312), without and with the rule: words 1,833 → 968 (−47 %), scanner markers 24 → 9, mean scanner score 78.4 → 87.8, em dashes 6 → 3, longest sentence 30 → 16 words. That `--setting-sources project` loads `CLAUDE.md` and `""` doesn't was checked separately with a secret word in the file. Small sample, one run per question: hypothesis.

Have the same issue in another language? Contribute a sibling recipe next to this one (lang: <code>).

## Related
- [Clean agent run with --setting-sources](../agent/agent-clean-run-setting-sources.md)
- [Humanize the script before TTS](text-humanize-script-before-tts.md)
