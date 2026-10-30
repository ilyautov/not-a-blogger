---
id: transitions-scene-swap-order
title: Swap scenes in order — text out, background changes, new text in
section: transitions
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
The next scene's background switches on while the previous text is still visible (light text over light background). A chapter sting fights the camera for the same `x`.

## Do
1. Order: text fades out → background changes → next text comes in.
2. Put a sting (graphic interstitial) only at a chapter boundary with a pause; inside a chapter there is no room.
3. Never let a sting and the camera shot animate the same property of the same container.

```js
function swap(t, from, to, bgFrom, bgTo) {
  tl.to(from, { autoAlpha: 0, duration: 0.15 }, t)
    .to(bgFrom, { autoAlpha: 0, duration: 0.2 }, t + 0.15)
    .fromTo(bgTo, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2 }, t + 0.15)
    .fromTo(to, { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.3, ease: "power3.out" }, t + 0.35);
}
```

## Verify
Dry frames at every boundary: no frame shows old text on the new background.

## Don't
Skip strict ordering only when text and background share one fill and contrast holds.

## Evidence
- A sting fits a chapter boundary with a 1.5 s pause; inside a chapter the gap between lines was 0.32 s, and sting + camera broke the frame.
- The order error was caught by dry frame review before render.
Gap figures describe one video; the order rule was checked by dry frame review, not by viewers. To promote: count broken frames at scene joints on N videos with the order enforced versus the earlier batch.

## Related
- [Dry frame review](../qa/qa-dry-frame-review.md)
- [Whip pan with motion blur](transitions-whip-pan.md)
