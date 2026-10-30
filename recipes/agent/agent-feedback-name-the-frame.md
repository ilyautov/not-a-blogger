---
id: agent-feedback-name-the-frame
title: Give the agent feedback that names the second, the defect and the action
section: agent
lang: any
status: hypothesis
evidence: experience
tools: [Claude Code, Codex]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-10-27
updated: 2026-10-29
contributors: [not-a-blogger]
---

## When
You watched the draft and something is off, and the first words that come are "make it nicer", "this part is boring", "more dynamic". The agent cannot act on that: it will change something random, re-render, and you will be back at the same frame.

## Do
1. Pause on the frame. Write down the time, the defect, the action. One note per defect.
2. Say what the next scene should do about it, so the fix does not push the ending off the clip.
3. Send the notes one at a time, or at most two or three per round, and wait for the re-render before the next.

```text
Was:    "It's kind of boring here."
Better: "At 0:06 the headline takes four lines. Cut it to two, bigger font,
         hold it one more second. Shift the next scene so the end isn't clipped."
```

Run this checklist over the whole draft before you write the notes; each "no" is one note:

1. Readable on a phone without zooming?
2. One idea per scene?
3. No empty frames and no accidental jumps (a cut you didn't plan, an element popping or vanishing mid-move)? Planned hard cuts are fine.
4. If there is a voice: words, stresses and line endings audible?
5. Every number on screen checked against its source? (Voice and screen may carry different information; the number doesn't have to be spoken.)

## Verify
The agent's reply quotes the timestamp from your note and names the file it changed (`scene/scene.ts`, a line in `voice/lines.json`), then shows the frame before and after. A reply without a timestamp or a file means it guessed. Check the frame at that second yourself in the new contact sheet.

## Don't
- Don't batch ten vague notes into one message; the agent will fix the easy ones and declare the rest done.
- Don't ask for "more dynamic", "livelier", "more professional": name the second where it drags and what should move.
- Don't let the agent decide the fix is complete: the frame at that second is the evidence, not the diff.

## Evidence
Experience from our own rounds: notes of the form "second, defect, action" were closed in one re-render, while "boring" and "make it nicer" cost two or three rounds and often moved the defect instead of removing it. Not counted; status stays hypothesis.

## Related
- [Review the middle frame of every scene before render](../qa/qa-dry-frame-review.md)
- [Review the final mp4 contact sheet yourself](../qa/qa-contact-sheet-final.md)
- [Ask the agent for an evidence log, not for its reasoning](agent-evidence-log-wording.md)
