---
id: brand-mascot-once-logo-last
title: Show the mascot once per episode on a fitting word, the logo only at the end
section: brand
lang: any
status: proven
evidence: measurement
tools: [GSAP]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A mascot sits in a corner the whole video, the logo stays as a watermark. That is slide chrome: viewers stop noticing, the frame reads as a presentation. Technical risk: a mascot anchored to a word can get stuck over later scenes.

## Do
1. Mascot appears once per episode, on the word where its role matches the line's meaning. It peeks from the edge and covers no diagram node; it is secondary to the frame's metaphor.
2. Logo and channel name appear at the very end, after the last line has played.
3. Mascot window ≥2.6 s: if the exit is scheduled before the entrance finishes, the completed tween holds final opacity and the mascot stays on screen.
4. At build time print one line per mascot appearance: the only way to spot sticking without watching the whole video.

```js
// t_in: anchor word, t_out: scene end
let show = t_in;
if (t_out - 0.2 - show < 2.6) show = t_out - 2.6;        // at least 2.6 s on screen
tl.fromTo('#mascot', { opacity: 0, x: 80 }, { opacity: 1, x: 0, duration: .4 }, show);
tl.to('#mascot', { opacity: 0, duration: .2 }, t_out - 0.2);
console.log(`mascot: ${fmt(show)} - ${fmt(t_out)} (${(t_out - show).toFixed(1)} s)`);
```

## Verify
Build log has one line per mascot appearance, each ≥2.6 s and inside its own scene.

## Don't
- Don't apply "once per episode" to a skit where the mascot is the main character: it's in frame by plot.

## Evidence
The anchor fell on a scene's last word, the exit was scheduled before the entrance finished, and the mascot hung over other scenes for almost six minutes (9:48 to 15:41 of a long video). The bug shipped in two versions in a row; both were re-rendered.

## Related
- [Stickers outside the camera](brand-stickers-outside-camera.md)
- [Review the final contact sheet yourself](../qa/qa-contact-sheet-final.md)
- Example: [A hook that blocks a dangerous command](../../examples/hook-vertical-from-long/README.md)
