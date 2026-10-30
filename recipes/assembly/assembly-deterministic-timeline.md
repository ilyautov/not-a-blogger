---
id: assembly-deterministic-timeline
title: Make every frame a pure function of time — no Date.now, no unseeded random
section: assembly
lang: any
status: hypothesis
evidence: experience
tools: [GSAP, JavaScript]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Preview and render diverge: particles elsewhere, different shake, elements appear in wrong places on seek. Frame-by-frame rendering seeks the timeline; randomness and wall-clock time break it.

## Do
1. One paused timeline per scene; the renderer seeks it.
2. No `Math.random()`, `Date.now()`, `performance.now()` inside a frame. Randomness = seeded LCG; shake = sum of sines.
3. No relative `+=` tweens on properties someone else animates.
4. Animate `transform` and `opacity`.
5. No variable-step physics; if physics is needed, use a fixed-step engine.

```js
function lcg(seed) { let s = seed >>> 0; return () => (s = (1664525 * s + 1013904223) >>> 0) / 2 ** 32; }
const rnd = lcg(42);
const dots = Array.from({ length: 120 }, () => ({ x: rnd() * 1920, y: rnd() * 1080 }));
const tl = gsap.timeline({ paused: true });
window.__timelines = window.__timelines || {}; window.__timelines["scene"] = tl;
```

## Verify
Render one frame twice (e.g. t = 7.3 s) and compare PNG hashes.

## Don't
Don't play timelines in real time during render; let the renderer seek.

## Evidence
No measurements: rule taken from the contracts of open-source HTML-to-video renderers and a camera-moves reference.

## Related
- [Handheld camera via sines](../camera/camera-handheld-sines.md)
- [Tween lifetime](assembly-gsap-tween-lifetime.md)
