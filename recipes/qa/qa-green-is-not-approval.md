---
id: qa-green-is-not-approval
title: Don't treat green automated QA as approval of the video
section: qa
lang: any
status: proven
evidence: measurement
tools: []
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-29
contributors: [not-a-blogger]
---

## When
The agent builds a video, all checks (audio, ASR, timing, scene contract, motion lint) are green, and it reports "done". The viewer or client sees slop, a presentation, or empty frames.

## Do
1. Separate statuses: "technically built" → "artistically accepted by a human" → "publishing allowed". Each is set by its own person.
2. Before showing, review the contact sheet and play the whole video yourself.
3. Before a new production, re-read recorded rejections and feedback on past videos.
4. Publishing is the person's step, never the agent's ([AGENTS.md](../../AGENTS.md), rule 5). The agent stops at a local package: the final file, title, description, checklist and the QA report, and tells the person what is left to do.

## Verify
The video's metadata carries a status, "accepted" was not set by the agent, and the agent's last action was preparing the local package, not an upload.

## Don't
- Don't report "done" or "ready" on green checks alone.
- Don't drop automated checks: they catch technical defects cheaply; they just don't answer "is it worth watching".

## Evidence
- A video that passed 15 green checks was rejected: it had no event worth watching.
- 27-minute video with green checks: 22% of runtime empty background.
- A 2:11 video with green QA: "everything is very bad"; the agent hadn't looked at frames before showing.
The 22 % figure is the frame-fill measurement of one 27-minute video; the other two are counted rejections of videos with green checks (15 checks; 2:11 reel).

## Related
- [Final contact sheet](qa-contact-sheet-final.md)
- [Script before build](../idea/idea-script-before-build.md)
