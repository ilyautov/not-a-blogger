---
id: qa-dry-frame-review
title: Review the middle frame of every scene before render
section: qa
lang: any
status: proven
evidence: measurement
tools: [Playwright, ffmpeg]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
Rendering a long video takes hours, and a layout defect is baked into the mp4 afterwards. Automated checks don't look at layout at all.

## Do
1. Before synthesis, check that scene line ranges don't overlap.
2. Before render, capture the middle frame of each scene straight from HTML (timeline seek) and build contact sheets.
3. Review sheets by eye; open suspicious frames at full resolution (a pill overflow is invisible at 640×360).
4. Check numbers on screen against the source as strictly as numbers in speech.

```bash
# mid-scene frames captured by script, into 4×3 sheets
ffmpeg -pattern_type glob -i "qa/mid/*.png" -vf "scale=640:-1,tile=4x3" qa/mid_sheet_%02d.jpg
```

## Verify
Every sheet reviewed; found defects written down and fixed before render starts.

## Don't
- Don't treat dry frames as a substitute for the final contact sheet: stuck elements (tweens outliving a scene) don't show here.
- Don't skip character hand poses on stills: a "pointing" gesture read as the middle finger. Index finger diagonal to the side, thumb out, hand in three-quarter view; show the finger only after the arm has settled on the diagonal. One case, caught on a 2 fps sheet before showing anyone.

## Evidence
31-minute long-form: dry review of 104 frames found six layout defects (two scenes on top of each other, a pill off the edge, overlapping elements, an extra barrier, an underline across the whole card, a sticker cut by the edge) and two invented numbers.

## Related
- [Final contact sheet](qa-contact-sheet-final.md)
- [Fact-check file per video](../idea/idea-factcheck-file.md)
- Example: [TV ads switched off](../../examples/tv-no-ads/README.md)
