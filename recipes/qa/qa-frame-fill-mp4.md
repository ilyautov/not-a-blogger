---
id: qa-frame-fill-mp4
title: Measure frame fill on the rendered mp4, not in the DOM
section: qa
lang: any
status: proven
evidence: measurement
tools: [ffmpeg, Python, Pillow, numpy]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Technical checks are green, the stillness lint is silent (captions change every half second so the frame looks "alive"), yet a large share of the video is empty background with captions. DOM measurement lies: a 1300×90 pill chain counts as "wide".

## Do
1. **Empty-frame check.** Run `tools/qa/frame_fill.py` in `fill` mode on the finished mp4. One definition for the whole kit ([QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md)): a frame every 2 s, the bottom 14 % (captions) excluded, a pixel is ink when it differs from the frame median by more than 26, a frame is empty below 4 % ink, empty runs are reported from 6 s. The band is a fraction of the height, so the same call works for vertical video.

```bash
python3 tools/qa/frame_fill.py final.mp4 --json qa/frame-fill.json --fail-on-empty
```

2. **Grid fill.** The same tool in `grid` mode: 16×8 cells (`--cols 8 --rows 16` for vertical), bottom 14 % excluded, a cell counts when 1.2 % of its pixels are ink. Track median and p10 per video and per scene type; compare with your own accepted videos, there is no universal pass line.

```bash
python3 tools/qa/frame_fill.py final.mp4 --mode grid --json qa/frame-grid.json            # horizontal 16×8
python3 tools/qa/frame_fill.py final.mp4 --mode grid --cols 8 --rows 16 --json qa/frame-grid.json  # vertical
```
3. For a pre-render estimate via page seeking, reload the page every ~50 seeks (it stops repainting).

## Verify
Empty-frame share near zero; median fill not below previous videos viewers accepted.

## Don't
Don't measure without cropping the caption strip: captions count as content and the result is optimistic. Don't re-implement the pixel rule with your own numbers: the 22 % figure below was taken with an earlier ad-hoc definition (step 3 s, diff > 28, < 1 %), and two definitions can't be compared.

## Evidence
- 27-minute video with green checks: 22% of runtime (6 minutes) empty background, sixteen holes longer than 9 s, the longest 33 s.
- DOM measurement said 20.5% fill, mp4 measurement 25%, and gaps remained.
- Viewer-accepted video: median fill 78%, p10 73%; long-form on the old pill grammar: 24% and 13%.

## Related
- [Stillness lint](qa-still-lint.md)
- [Empty scene start](../assembly/assembly-no-empty-scene-start.md)
- [Content proportion](../assembly/assembly-content-proportion.md)
- Example: [Agent said tests passed](../../examples/agent-cheats-long/README.md)
