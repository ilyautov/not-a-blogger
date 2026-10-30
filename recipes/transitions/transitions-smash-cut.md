---
id: transitions-smash-cut
title: Open with a smash cut from silence to impact
section: transitions
lang: any
status: hypothesis
evidence: experience
tools: [GSAP, ffmpeg]
learn: ../../learn/en/05-camera-editing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The hook starts smoothly; the first second doesn't grab.

## Do
1. Contrast everything at once: wide vs close, still vs shake, silence vs impact.
2. Make the quiet part truly quiet.
3. Impact SFX and a short whoosh land exactly on the cut frame, zero frame offset.
4. 2D variant: a sharp zoom onto a huge object (key, number) for ~0.5 s around the event.

```js
tl.set("#calm", { autoAlpha: 0 }, tCut)
  .set("#loud", { autoAlpha: 1, scale: 1.3 }, tCut)
  .to("#loud", { scale: 1, duration: 0.16, ease: "power3.out" }, tCut);
// impact SFX starts exactly at tCut (frame-accurate)
```

## Verify
Waveform + frames: impact peak and shot change on the same frame.

## Don't
Don't let sound lead or lag by even one frame: it kills the impact.

## Evidence
No own measurements. A probe with a smash cut onto huge keys (0.55 s around the press) was built, no separate rating.

## Related
- [Result in the first second](../hooks/hooks-result-in-first-second.md)
- [J- and L-cuts](transitions-j-l-cut.md)
- Example: [Three keys, repeat (failed)](../../examples/three-keys-repeat/README.md)
