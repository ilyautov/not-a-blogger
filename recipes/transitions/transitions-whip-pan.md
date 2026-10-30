---
id: transitions-whip-pan
title: Hide a cut inside a whip pan with motion blur
section: transitions
lang: any
status: hypothesis
evidence: experience
tools: [GSAP, Canvas 2D]
learn: ../../learn/en/05-camera-editing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Switching items or places by a plain cut looks limp; visible camera travel between shots looks like a jerk.

## Do
1. Hold 0.2 s, swing shot A away by 35–45° (in 2D a fast shift) over 0.3 s accelerating; bring B in from the same side over 0.3 s decelerating.
2. Blur proportional to speed, max ~8% of frame width; in HTML use several offset "ghosts".
3. Same direction for exit and entry.
4. Sound: noise whoosh with a rising band.
5. Hide shot changes inside one scene in the cut window too (~0.22 s), or the travel shows.

```js
const blurMax = 0.08 * 1920;                          // ~150 px
tl.to("#sceneA", { x: -1920, duration: 0.3, ease: "power2.in",
                   filter: `blur(${blurMax / 10}px)` }, tCut - 0.3)
  .fromTo("#sceneB", { x: 1920, filter: `blur(${blurMax / 10}px)` },
                     { x: 0, filter: "blur(0px)", duration: 0.3, ease: "power2.out" }, tCut);
```

## Verify
Frame at the joint: both scenes blurred in one direction, no white blob.

## Don't
Don't use too large an angle: the camera swings into emptiness and the blur becomes a white blob.

## Evidence
No retention measurements. Values from a camera-moves reference; the 0.22 s cut overlap verified on a long-form video with shot changes.

## Related
- [Hard cut by default](transitions-hard-cut-default.md)
- [Scene swap order](transitions-scene-swap-order.md)
- [SFX by meaning](../sound/sound-sfx-by-meaning.md)
