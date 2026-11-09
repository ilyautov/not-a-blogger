---
id: qa-ai-jury-edits-not-gate
title: Use an AI jury to generate up to three edits before showing the video, never as a gate
section: qa
lang: any
status: hypothesis
evidence: experience
tools: [Claude Code, Codex CLI]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-11-09
updated: 2026-11-09
contributors: [not-a-blogger]
---

## When
The video passed technical QA and is about to go to the person. You want one more look that is not yours, but a
"score ≥ 7 = ship" rule would let a model approve art.

## Do
1. After QA, start a fresh agent that did not build the video. Give it only what exists: the contact sheet, up to
   three full frames, the brief with its "never do" list and its reference comparison. No new render, no new metrics.
2. Use [the jury prompt](../../prompts/agent/ai-jury-edits.md): seven questions (hook, hero moment, template frame,
   weakest 5 seconds, sound on picture, generated-sounding words, copy of the reference), each with a timestamp.
3. Take at most three edits, the biggest first, each as timestamp → what → how in numbers. At least one must raise
   the "wow", not only fix.
4. Apply in one round the edits that touch nothing the person approved and need no new voice; re-check by frames.
   Pass the rest to the person in one line: "the jury suggests: …".

## Verify
`qa/jury.md` has seven timestamped answers, ≤ 3 edits with numbers and one score; `qa/final-result.json` has no field
derived from the score; the message to the person lists what was applied and what is only suggested.

## Don't
- Don't run a second jury round on the same video: after the person has seen it, only their feedback drives edits.
- Don't put the score into QA or into the status as approval.
- Don't let the jury change approved elements (voice, character, palette) on its own.

## Evidence
No measurement yet: written after the author's pipeline adopted it from two neighbouring kits (sarpstar/cinecode,
`references/jury.md`, MIT; Vincentwei1021/mg-styles-15, `rubric.md`, MIT). The "not a gate" part rests on the
author's calibration of automatic checks, where no metric separated approved from rejected videos
([picture checks as warnings](qa-picture-checks-warn-only.md)). To promote: count jury edits the person kept against
edits they reverted over 10 videos.

## Related
- [Green QA is not approval](qa-green-is-not-approval.md)
- [Review the final contact sheet yourself](qa-contact-sheet-final.md)
- [≥ 4 of 6 parameters differ from the reference](../idea/idea-four-of-six-differ.md)
