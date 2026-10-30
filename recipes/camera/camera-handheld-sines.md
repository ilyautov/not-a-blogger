---
id: camera-handheld-sines
title: Build handheld camera as a sum of sines on a separate layer
section: camera
lang: any
status: hypothesis
evidence: experience
tools: [GSAP, Canvas 2D, Three.js]
learn: ../../learn/en/05-camera-editing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A static camera makes the frame dead; per-frame random offsets look like digital jitter; relative (`+=`) micro-hits on the same container as the camera shot conflict with it.

## Do
1. Shake = sum of 2–3 low-frequency sines, never `Math.random()`. Use frequencies that are multiples of the loop length for a seamless loop.
2. Defaults: position ±2–3 cm in 3D (about ten px in 2D), rotation ±0.5°.
3. On impact: a short seeded noise burst for 1–1.5 s.
4. Put shake and hits on a wrapper layer (`#shake`); keep the camera shot on `#world`.
5. For calm scenes instead: slow diagonal drift with 2–3° rotation over 5 s, `power1.inOut`.

```js
const L = 4.7, w = 2 * Math.PI / L;               // loop length, s
function handheld(t, a = 12) {                      // a = amplitude, px
  const x = a * (0.6 * Math.sin(w * t) + 0.4 * Math.sin(3 * w * t + 1.3));
  const y = a * (0.5 * Math.sin(2 * w * t + 0.7) + 0.5 * Math.sin(5 * w * t));
  const r = 0.5 * Math.sin(w * t + 2.1);           // degrees
  return { x, y, rotation: r };
}
// every frame: gsap.set("#shake", handheld(t)); #world moves only the shot
```

## Verify
Shake is identical in preview and render (frame = pure function of time); no jerks on the contact sheet.

## Don't
Don't add shake to a dolly zoom or to frames with small text: the eye needs smooth motion to read.

## Evidence
No own measurements. Defaults from a camera-moves reference: ±2–3 cm, ±0.5°, impact 3–5 cm for 1–1.5 s; drift 2–3° over 5 s from the storyboard of an open launch video.

## Related
- [Parallax by depth formula](camera-parallax-formula.md)
- [Deterministic timeline](../assembly/assembly-deterministic-timeline.md)
- Example: [TV ads switched off](../../examples/tv-no-ads/README.md)
