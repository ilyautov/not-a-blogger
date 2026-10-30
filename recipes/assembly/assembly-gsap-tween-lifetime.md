---
id: assembly-gsap-tween-lifetime
title: Never let a tween outlive its scene
section: assembly
lang: any
status: proven
evidence: measurement
tools: [GSAP]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
A finished GSAP tween holds its end value. If an element's exit is scheduled before its entrance ends, it stays on top of later scenes. Same family: `tl.set` does not survive a neighbour's finished tween; a container with CSS `opacity:0` won't appear from animating its children; inline `transform: scale()` conflicts with a `scale` tween.

## Do
1. Clamp every move in a scene to `t_out − 0.30`.
2. If entrance-to-exit is too short, move the entrance earlier, not the exit later. Log every character appearance window in the build log.
3. Instead of `tl.set` after another tween, use a short 0.08 s tween.
4. Animate a CSS-hidden container itself.
5. Set the initial scale in `fromTo`, not inline.

```js
const OUT_PAD = 0.30, MIN_SHOW = 2.6;
function show(el, tIn, tOut) {
  let a = tIn; const b = tOut - 0.2;
  if (b - a < MIN_SHOW) a = b - MIN_SHOW;
  console.log(`${el}: ${a.toFixed(2)} – ${b.toFixed(2)}`);
  tl.fromTo(el, { autoAlpha: 0, scale: 0.94 }, { autoAlpha: 1, scale: 1, duration: 0.3 }, a)
    .to(el, { autoAlpha: 0, duration: 0.15 }, Math.min(b, tOut - OUT_PAD));
}
```

## Verify
Build log lists appearance windows; final mp4 contact sheet one minute after an exit shows no element.

## Don't
- Don't let scenes overlap in line ranges: elements of both scenes will be on screen regardless of tweens. Check ranges at build time.
- Don't rely on a tween for what must be visible on frame 0: on `seek(0)` GSAP does not apply tweens that start at 0, so the first frame shows the pre-tween state. Set the frame-0 state in CSS (experience, no case count).

## Evidence
A character overlay whose exit came before its entrance ended hung over other scenes for almost six minutes; the video was re-rendered twice.

## Related
- [Blink with color, not opacity](../captions/captions-blink-color-not-opacity.md)
- [Deterministic timeline](assembly-deterministic-timeline.md)
