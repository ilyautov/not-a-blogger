---
id: image-seamless-loop-bg
title: Loop a background clip by blending its tail into its head, and measure the seam
section: image
lang: any
status: hypothesis
evidence: measurement
tools: [ffmpeg, tools/qa/seam.py]
learn: ../../learn/en/04-image-and-frame.md
added: 2026-10-28
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
A short format plays on repeat (a text card over b-roll, a 7–8 s loop): viewers see the jump where the clip restarts. Generated or archive clips don't end where they began.

## Do
1. Take a clip about 1 s longer than the loop (9 s for an 8 s loop). Prefer a shot with a static camera and cyclic motion (hands typing, a machine, rain).
2. Build the loop so its first second is a crossfade from the clip's tail (8–9 s) into its head (0–1 s), followed by 1–8 s as is. The loop's last frame is then source 7.99 s and its first frame blends into source 8.0 s: no jump.
3. Measure the seam: the difference last→first frame against the median difference of neighbouring frames.

```bash
ffmpeg -i clip.mp4 -filter_complex "\
[0:v]split=3[a][b][c];\
[a]trim=8:9,setpts=PTS-STARTPTS[tail];[b]trim=0:1,setpts=PTS-STARTPTS[head];\
[tail][head]blend=all_expr='A*(1-T)+B*T'[x];\
[c]trim=1:8,setpts=PTS-STARTPTS[mid];\
[x][mid]concat=n=2:v=1,fps=30,format=yuv420p[v]" -map "[v]" -frames:v 240 loop.mp4
python3 tools/qa/seam.py loop.mp4          # exit 1 when seam > 2 × median neighbour difference
```

## Verify
`seam.py` passes (ratio ≤ 2), and a contact sheet of the loop played twice in a row shows no jump at the joint.

## Don't
- Don't loop a clip with a camera push or pan: the crossfade shows two framings at once. Pick another clip.
- Don't crossfade longer than 1 s: double exposure becomes visible.
- Don't take the 2× threshold as measured: it was chosen from four accepted loops.

## Evidence
Four 8 s loops (generated video, a 3D render, archive footage, flat 2D) built 28 Oct 2026: seam / median neighbour difference 1.02, 1.16, 1.31 and 1.70. A second generated clip with a camera push was dropped: it didn't loop. The loops have not been reviewed by the owner or published, hence hypothesis.

## Related
- [Period footage from archive.org](image-archive-footage-prelinger.md)
- [Frame review before render](../qa/qa-dry-frame-review.md)
