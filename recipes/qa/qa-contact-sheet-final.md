---
id: qa-contact-sheet-final
title: Review the final mp4 contact sheet yourself before showing it, even when the agent's QA is green
section: qa
lang: any
status: proven
evidence: measurement
tools: [ffmpeg, Claude Code]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
Half of the defects show only in the finished file: a stuck element, blinking, a shape covering a caption, empty scene starts, slide-like layouts. The agent's checks (loudness, ASR, contract tests) measure sound and structure, not the picture, so it says "done" with green QA and misses them.

## Do
1. After render, build sheets from the final mp4: one frame every 4 s, 6×6 per sheet. Short videos: every 2 s.
2. Review them yourself; don't hand them to another agent "to look at". Open suspicious frames at full resolution.
3. In the agent's task, separate statuses: "technical status" (QA passed) ≠ "ready to show". A human sets readiness after the sheet.

```bash
ffmpeg -loglevel error -i final.mp4 -vf "fps=1/4,scale=320:-1,tile=6x6" qa/sheet_%02d.jpg   # long video: several sheets
ffmpeg -loglevel error -i final.mp4 -vf "fps=1/2,scale=320:-1,tile=6x2" qa/short_sheet_%02d.jpg
ffmpeg -loglevel error -ss 00:00:12 -i final.mp4 -frames:v 1 qa/frame-12s.png             # full frame at a suspicious second
```

## Verify
Every sheet reviewed, findings written down. No sheet has empty frames, text overlaps, or frames that look like a slide with a title and bullets.

## Don't
- Don't judge small overflows from a 320 px-wide sheet.
- Don't use a 4 s step for fast cutting: it misses flashes shorter than the step. Use `fps=1` or frames at cuts (`select='gt(scene,0.3)'`).

## Evidence
- A long video passed audio verify (−15.2 LUFS, 0 word misses, contract tests 6 of 6), yet 26 % of runtime was a half-empty frame; found only on the sheet.
- Batch of five videos from parallel agents: in one a caption overlapped a shape; the agent missed it, found only by frame review.
- A blinking word stuck until the end of the video was found only on the final mp4 sheet; three consecutive empty frames at scene starts showed on fps=1/2 sheets.
- A 2:11 reel with green agent QA, delivered without frame review, was rated "everything is very bad".

## Related
- [Dry frame review before render](qa-dry-frame-review.md)
- [Green QA is not approval](qa-green-is-not-approval.md)
- [Check a deck PDF with a contact sheet](../slides/slides-check-pdf.md)
- [Script before build](../idea/idea-script-before-build.md)
