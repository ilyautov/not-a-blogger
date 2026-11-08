---
id: assembly-frames-before-draft-render
title: Check a frame sheet before a draft render; on short videos a draft saves almost no time
section: assembly
lang: any
status: hypothesis
evidence: measurement
tools: [HyperFrames, ffmpeg]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-11-08
updated: 2026-11-08
contributors: [not-a-blogger]
---

## When
You want a fast look at the layout before the final render, and the usual advice says "render a draft first: lower
quality, lower fps, a short fragment".

## Do
1. Look at frames first, not at a video. In `starter/`: `./make.sh frames` writes a frame every 0.75 s to
   `qa/frames/sheet-N.jpg`; `tools/render.py --frames 0.75 --from 10 --to 20` limits it to one span. Layout, text size
   and overlaps show up on a sheet.
2. For a video under about a minute, skip the draft and render at the final settings: Chrome startup and page load
   dominate, so `--quality draft`, half the fps or `--end 5` win a few seconds at most.
3. Use a draft only where capture time is the cost: a long video or a heavy scene (WebGL, large images, blur). Measure
   both renders once on your machine before you make the draft a habit.

```bash
# time a final and a draft render of the same project
time npx --yes hyperframes@0.9.23 render -q looks --fps 30 -o out/final.mp4
time npx --yes hyperframes@0.9.23 render -q draft --fps 15 -o out/draft.mp4
```

## Verify
Both timings are written next to the project. If the draft is not at least twice as fast, drop it from the routine and
rely on the frame sheet.

## Don't
- Don't judge motion from a 15 fps draft: easing and camera moves look different at the final frame rate.
- Don't treat a frame sheet as the final check: tweens that outlive a scene only show in the finished mp4
  ([final contact sheet](../qa/qa-contact-sheet-final.md)).

## Evidence
`starter-lite/`, 15 s, 1080×1920, Apple M1 Max, measured 2026-11-08:
- hyperframes 0.8.208: `looks` 30 fps 11.9 s and 10.3 s; `draft` 30 fps 10.2 s; `draft` 15 fps 9.1 s and 7.7 s. The
  draft file at 30 fps was larger (652 KB vs 612 KB): `draft` changes encoder settings, not capture.
- hyperframes 0.9.23: full 15 s 15.5 s and 8.6 s; `--end 5` (5 s of the 15) 15.0 s and 14.8 s; at 60 fps full 15.5 s,
  `--end 5` 21.6 s. The fragment was not faster.

One light project, two runs per setting, noisy timings. To promote: repeat on a 60 s+ video and on a WebGL scene, at
least three runs each.

## Related
- [Review the middle frame of every scene before render](../qa/qa-dry-frame-review.md)
- [Serialize heavy jobs](assembly-serialize-heavy-jobs.md)
