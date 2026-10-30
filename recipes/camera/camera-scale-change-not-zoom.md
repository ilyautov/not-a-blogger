---
id: camera-scale-change-not-zoom
title: Change shot scale with a cut per line instead of a six-percent zoom
section: camera
lang: any
status: hypothesis
evidence: viewer-feedback
tools: [GSAP]
learn: ../../learn/en/05-camera-editing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
One shot scale for the whole video with a smooth zoom inside it; each new line looks like a new slide.

## Do
1. Change shot scale with a hard cut on every line. Define the shot by a point of interest in image fractions: `shot(t, u, v, s)`.
2. Inside a shot: slow drift.
3. Use a wide scale range, 0.96–1.55, with pans between points of interest.
4. Under numbers, push the frame to `blur(9px)` with brightness 0.74 and **bring it back** when speech returns to the picture.
5. At deep push-in dim the far plane: `opacity .16`, `blur 7px`.

```js
function shot(t, u, v, s, dur = 0.01) {      // u,v = image fractions 0..1
  const W = 3240, H = 2160;                    // image larger than frame
  tl.to("#world", { scale: s, x: 960 - s * u * W, y: 540 - s * v * H, duration: dur }, t);
}
shot(0.0, 0.50, 0.50, 0.96);  // wide
shot(2.4, 0.62, 0.40, 1.55);  // close, hard cut
tl.to("#world", { filter: "blur(9px) brightness(0.74)", duration: 0.3 }, 5.1)
  .to("#world", { filter: "blur(0px) brightness(1)",   duration: 0.3 }, 7.6);
```

## Verify
On the contact sheet adjacent lines differ in shot scale; no scene holds one shot longer than one line.

## Don't
Don't force full-screen cuts on screen-based top-N formats (shortcuts, commands): there a two-zone layout with a live background won.

## Evidence
No retention measurements. A 1.0 → 1.06 zoom over 5 s was rejected as "static"; a probe with 0.96–1.55 scale and pans was shown as the new grammar, no verdict yet.

## Related
- [No Ken Burns](camera-no-ken-burns.md)
- [One zone, no chrome](../transitions/transitions-one-zone-no-chrome.md)
- [Keep the hero in frame](camera-keep-in-frame.md)
- Example: [Whole course in 20 minutes (failed)](../../examples/course-retelling/README.md)
