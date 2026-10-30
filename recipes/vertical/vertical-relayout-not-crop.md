---
id: vertical-relayout-not-crop
title: Make a short from a long video by re-layout, not crop
section: vertical
lang: any
status: proven
evidence: measurement
tools: [ffmpeg, GSAP]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Shorts are cut from a horizontal long video: the frame is letterboxed inside a vertical canvas or center-cropped. Text on a phone ends up smaller than in the long video, and a video strip with a title above and caption below is a second zone, i.e. a slide.

## Do
1. Keep audio as is: same takes, same alignment, same line timing.
2. Move the chosen segment's timeline into a new 1080×1920 project and re-lay out every scene for vertical.
3. Make wide things tall: loop 860×370 → 680×620 with smaller node font; code card → 800 px wide; drop optional parts of long commands.
4. Align content center with screen center, not the bottom.
5. Recompute the long video's camera shots too; shots that spread content full width hurt vertical.

```bash
# measure how wide the long video's content really is (per second)
ffmpeg -i long.mp4 -ss 120 -t 30 -vf "fps=1,cropdetect=limit=24:round=2" -f null - 2>&1 | grep -o "crop=[0-9:]*" | sort | uniq -c | sort -rn | head -3
```

## Verify
Main text font in the short is larger than in the long; mp4 grid fill not below the long.

## Don't
Don't crop or letterbox the horizontal render.

## Evidence
- Horizontal scene content spans ~1620 of 1920 px (median over four clips, 1588–1708).
- Cropping to real bounds gives 0.62–0.67× scale, fitting the whole frame 0.56×: text smaller than in the long.
- Two series of four re-laid-out shorts: median fill 27–37% (not worse than their long) and 33–43% vs 24% for their long.

## Related
- [Keep everything in P ± (W/2)/s](../camera/camera-keep-in-frame.md)
- [Titles on the joint and gaps](vertical-titles-on-joint.md)
- [One zone in frame](../transitions/transitions-one-zone-no-chrome.md)
- Example: [Hook that blocks a dangerous command](../../examples/hook-vertical-from-long/README.md)
