---
id: camera-keep-in-frame
title: Compute the camera shot with the screen formula so the hero never leaves the frame
section: camera
lang: any
status: hypothesis
evidence: experience
tools: [GSAP]
learn: ../../learn/en/05-camera-editing.md
added: 2026-10-23
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
A 1.35–1.5 push-in on a 1580-wide card pushes its edges off screen; a shot center right of 960 sends the left column off screen. After moving to vertical, push-ins that were safe at 1920 cut edge nodes in half, a diagram's outcome overflows the right edge. Half-cut cards at the edge read as a bug.

## Do
1. Screen x of a world point for shot center `P`, scale `s` and frame width `W`: `screen = W/2 + s · (world − P.x)`. Horizontal 1920: `960 + s·(world − P.x)`; vertical 1080: `540 + s·(world − P)`.
2. Keep everything that must stay visible inside `P.x ± (W/2) / s`. Size the hero from this formula before layout: at a 1.35 peak only 800 px of a 1080-wide frame are visible, at 1.48 about 730 px.
3. World offset = `(W/2 − center) × scale`; horizontal: keep `|960 − center| ≤ 160`; vertical: center not below 1000.
4. Two different numbers, don't mix them: the *resting* scale while the hero sits at an edge stays ≤ 1.05 (horizontal) or ≤ 1.04 (vertical), hero edge ≥ 180 px from the frame edge; *push-in peaks* (1.35–1.5) are allowed only where step 2 says the hero still fits. In vertical, reduce peaks (one short: 1.55 → 1.35).
5. Set the initial scale in `fromTo`, not as an inline style next to a `scale` tween. UI elements (counters, captions) live outside the moving world.
6. Vertical re-layout: move labels from the right of an object to below it; shorten rails and lanes.

```js
function fits(box, P, s, W = 1920) {           // W = 1080 for vertical
  const half = W / 2 / s;
  return box.x0 >= P.x - half && box.x1 <= P.x + half;
}
console.assert(fits({ x0: 170, x1: 1750 }, { x: 960 }, 1.35), "card does not fit at push-in");
console.assert(fits({ x0: 140, x1: 940 }, { x: 540 }, 1.35, 1080), "800 px card at 1.35 in vertical");
```

## Verify
Dry frames at the peak of every push-in: no hero edge, node or label is cut.

## Don't
- Don't leave neighbouring cards visible at the edge during a deep push-in: dim the background.
- Don't assume the formula covers the platform safe zone (buttons, caption at the bottom): check a frame with the UI overlay.

## Evidence
- A 1580-wide code card overflowed the frame at 1.35 push-in (horizontal).
- At deep push-in the far plane is dimmed to `opacity .16` + `blur 7px`, otherwise edge cards look like defects.
- Vertical: a code card was narrowed to 800 px at 24 px font because at a 1.48 push-in it was wider than the frame; 800 px is exactly what fits at the reduced 1.35 peak (1080 / 1.35). A rail was shortened from 820 to 420 px, otherwise the outcome overflowed at 1.1 push-in.
- These are layout fixes on three videos, no outcome counted. To promote: run the `fits` assertion over N finished scenes and count cut edges on dry frames with and without it.

## Related
- [Change shot scale instead of zoom](camera-scale-change-not-zoom.md)
- [Re-layout, not crop](../vertical/vertical-relayout-not-crop.md)
- Example: [Hook that blocks a dangerous command](../../examples/hook-vertical-from-long/README.md)
