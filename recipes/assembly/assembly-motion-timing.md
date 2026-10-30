---
id: assembly-motion-timing
title: Set durations, easing and stagger from a table, not one value
section: assembly
lang: any
status: hypothesis
evidence: experience
tools: [GSAP]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Every element moves with one ease, on one axis, in the same 0.55 s. Viewers call it "angular and primitive".

## Do
1. At least three ease characters per composition.
2. Entrances: `ease-out` / `expo.out`; exits twice as fast as entrances.
3. Durations: UI motion 0.3–0.5 s `power2.out`; hero entrance 0.8–1.2 s `power3/4.out`; background `sine.out`; linear only for camera and mechanics.
4. Stagger 30–100 ms per item, whole group within 0.5 s: `items × stagger ≤ 0.5`.
5. Never `scale(0)`: start at 0.94.
6. Large text: letter-spacing −0.02em.

```js
const stag = Math.min(0.08, 0.5 / items.length);
tl.from(items, { y: 30, autoAlpha: 0, scale: 0.94, duration: 0.4, ease: "power2.out", stagger: stag }, t)
  .from(hero,  { y: 80, autoAlpha: 0, duration: 1.0, ease: "power4.out" }, t + 0.1)
  .to(items,   { autoAlpha: 0, duration: 0.2, ease: "power2.in" }, tOut - 0.2);
```

## Verify
Timeline lint: ≥ 3 ease families, non-zero duration spread, stagger in every group.

## Don't
Don't expect good easing to fix a slide layout: a video with correct easing still got "feels like a presentation".

## Evidence
No own retention measurements. Values compiled from an open-source renderer's doctrine, third-party easing guides and UI-motion rules; the source videos had one ease and 0.55 s for everything.

## Related
- [One zone in frame](../transitions/transitions-one-zone-no-chrome.md)
- [Deterministic timeline](assembly-deterministic-timeline.md)
