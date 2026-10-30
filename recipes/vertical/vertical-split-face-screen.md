---
id: vertical-split-face-screen
title: For screen-based top-N formats put the host on top and the screen below
section: vertical
lang: any
status: proven
evidence: ab-test
tools: [GSAP, ffmpeg]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The "one zone in frame" rule is applied mechanically to videos about shortcuts, commands and tools. A full-screen version with cuts "key → terminal → character" comes out worse than a plain split.

## Do
1. Screen formats (top-N shortcuts, commands, tools): host or character in a circle on top, screen below.
2. Live background, handheld camera, whip pans between items.
3. Captions without bars: outline and shadow.
4. Crop the terminal narrow (about 700–900 px of source), or text is small.

```bash
# split: top = host, bottom = screen recording
ffmpeg -i host.mp4 -i screen.mp4 -filter_complex \
 "[0]scale=1080:840,setsar=1[top];[1]crop=860:900:200:100,scale=1080:1080,setsar=1[bot];[top][bot]vstack" split.mp4
```

## Verify
Terminal text is readable on a phone; A/B against your own full-screen version.

## Don't
Don't use the split for story videos (narrative, skit): there it becomes a slide again; use one zone.

## Evidence
- A/B on one shortcuts video: the two-zone version beat the full-screen one ("the previous one was better after all"), despite a "presentation feel" remark about it.
- In a niche hits sample, the "host on top, screen below" format appears among top videos: 437k and 250k views.

## Related
- [One zone in frame](../transitions/transitions-one-zone-no-chrome.md)
- [Foreign thesis and refrain](../hooks/hooks-foreign-thesis-refrain.md)
- Example: [Three keys, repeat (failed)](../../examples/three-keys-repeat/README.md)
