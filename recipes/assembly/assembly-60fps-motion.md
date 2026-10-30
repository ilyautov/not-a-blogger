---
id: assembly-60fps-motion
title: Render motion-heavy reels at 60 fps, set in one place for every stage
section: assembly
lang: any
status: hypothesis
evidence: experience
tools: [ffprobe, ffmpeg]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-28
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
The video relies on motion: kinetic type, a moving camera, trajectories, particles. At 30 fps with no post-processing it reads as cards, and viewers say "there's no motion design".

## Do
1. Store fps once, in the project's config (story or composition file), and set it to 60 for motion reels.
2. Make every stage read that field: the renderer, the vertical re-layout and the final verify. No stage keeps its own hard-coded 30.
3. Keep timings in seconds, not frames, so switching 30 ↔ 60 doesn't change the timeline.
4. Leave deliberately low frame rates alone: a retro look built on 12–15 fps (see `templates/3d-skit/README.md`) stays low.
5. After rendering, build the contact sheet on the final mp4: motion mistakes (a stuck element, a camera pushing a column out of frame) only show there.

```bash
ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate,nb_frames -of csv=p=0 output/final.mp4   # 60/1,<frames>
ffmpeg -loglevel error -i output/final.mp4 -vf "fps=1/4,scale=320:-1,tile=6x6" qa/sheet_%02d.jpg
```

## Verify
`ffprobe` prints `60/1` for the final file and for every vertical cut made from it; frame count ≈ duration × 60.

## Don't
- Don't expect 60 fps alone to fix a slide layout or a static frame: it was one of four causes we named, not the main one.
- Don't raise fps on styles that need a low frame rate (retro console looks).

## Evidence
- A 15-second motion reel built in a separate session (1920×1080, 60 fps, nine sections, kinetic type, particles, trajectories) was the author's reference for "real motion"; the pipeline's 30 fps and zero post-processing was one of the four causes we found for the gap. The others: picture serving the voice line by line, 11 templates for 181 lines, the work never brought back into the pipeline.
- A 35-second probe at 60 fps on the new scene skeleton: grid occupancy 34% against 24% for the published long-form. A 2:07 long-form at 60 fps on the same skeleton: occupancy median 78%, praised by the author and published ([agent-cheats-long](../../examples/agent-cheats-long/README.md)).
- No A/B of 30 vs 60 fps with everything else equal; the gains above mix fps with layout changes: `hypothesis`.

## Related
- [Set durations, easing and stagger from a table](assembly-motion-timing.md)
- [Blink a word with color, not opacity](../captions/captions-blink-color-not-opacity.md)
- [Review the final contact sheet yourself](../qa/qa-contact-sheet-final.md)
- [Deterministic timeline](assembly-deterministic-timeline.md)
