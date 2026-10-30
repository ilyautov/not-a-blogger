---
id: text-local-edit-not-rewrite
title: Edit text locally instead of rewriting paragraphs "to make it livelier"
section: text
lang: any
status: proven
evidence: ab-test
tools: [humanizer-ru]
learn: ../../learn/en/02-text-humanizer.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
"Make it livelier" makes the model add emotions, particles, images and conclusions the author never had. The text gets punchy but foreign, with claims the author doesn't stand behind.

## Do
1. Mark specific spots: quote, what bothers the reader, action (keep, cut the wrapper, say it clearer, remove the duplicate).
2. Remove hard bans and markers by priority.
3. Add no new facts, emotions or images.
4. Check the result against the source claim by claim.

Prompt for an agent with the humanizer-ru skill (or any editing skill):

```text
Edit locally: mark specific spots and what to do with each.
Don't rewrite whole paragraphs, don't add emotions, images or facts
absent from the source. At the end: N markers before, M after.
```

## Verify
The diff is short replacements and deletions, not new sentences. Fact lock is clean.

## Don't
- Don't use "voice" quotas in the prompt: they produce a foreign intonation and staged rhetoric.
- Don't expect a local edit to save an empty source: it needs new text from the author.

## Evidence
Paired blind run in the humanizer-ru eval: 13 sources × 3 conditions (editor without skill, full skill with "voice" quotas, compact local edit) × 5 repeats = 195 answers, 195 blind ratings. "Voice" quotas gave a foreign intonation and staged rhetoric; the local edit had fewer meaning remarks. Limits: small sample, raters are agents, not people.

## Related
- [Before/after fact lock](text-fact-lock-before-after.md)
