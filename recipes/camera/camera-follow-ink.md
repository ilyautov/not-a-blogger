---
id: camera-follow-ink
title: Frame the camera on the actual text ink, not on the block's bounding box
section: camera
lang: any
status: proven
evidence: measurement
tools: [GSAP, Playwright, ffmpeg]
learn: ../../learn/en/05-camera-editing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Scene elements arrive one by one while the camera holds the full 1920×1080 canvas: the first seconds of each scene show one line in empty space. Block bounding boxes lie (a 1280-wide card may hold a 600-wide line).

## Do
1. Measure geometry by ink: `Range.getClientRects()` over text nodes, not the container's `getBoundingClientRect()`.
2. On each element entrance, pick a camera shot (scale `s`, center `P`) that fits the ink visible so far, with margins.
3. Hide each shot change inside a 0.22 s cut overlap; otherwise the pan jerk shows.
4. Build in two passes: scene → build → compute shots → scene → build.

```js
function inkBox(el) {
  const r = document.createRange(); r.selectNodeContents(el);
  const rects = [...r.getClientRects()].filter(q => q.width > 1 && q.height > 1);
  const x0 = Math.min(...rects.map(q => q.left)),  y0 = Math.min(...rects.map(q => q.top));
  const x1 = Math.max(...rects.map(q => q.right)), y1 = Math.max(...rects.map(q => q.bottom));
  return { x0, y0, x1, y1 };
}
// shot change inside the cut window
tl.to("#world", { scale: s, x: 960 - s * P.x, y: 540 - s * P.y, duration: 0.22, ease: "power2.inOut" }, tCut - 0.11);
```

## Verify
Measure frame fill on the rendered mp4, not in the DOM. A hole the camera cannot fix means the line has no picture: fix the content.

## Don't
- Don't trust DOM fill metrics as the final number.
- Don't try to fit a wide flat block (two-line quote, inline chain) by zoom; re-layout the content.

## Evidence
- Ink share of frame (excluding caption strip): median 11.2% → 20.5%; runtime below 6% fill: 29% → 5%; empty stretches longer than 6 s: 36 → 0.
- Measuring the rendered mp4 gave 25% instead of 20.5%: the DOM metric overstated, gaps remained.
- Camera at max scale 1.85 still left emptiness for a 1440×170 block: 16:9 cannot be filled by zoom.

## Related
- [Content proportion for the frame](../assembly/assembly-content-proportion.md)
- [Frame fill on the mp4](../qa/qa-frame-fill-mp4.md)
- [Keep the hero in frame](camera-keep-in-frame.md)
