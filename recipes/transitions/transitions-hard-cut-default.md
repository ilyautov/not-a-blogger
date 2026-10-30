---
id: transitions-hard-cut-default
title: Cut hard by default; keep showy transitions for 2–3 places
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
Every scene change gets a transition (crossfade, wipe, whip); pace drags and the video looks like slides with effects.

## Do
1. Default cut: hard.
2. Whip, dissolve, wipe: only at 2–3 key points (chapter change, "meanwhile", ending).
3. Dissolve 0.8–1.2 s, ease in-out, only for a time jump and the end card.
4. Wipe: one direction for the whole video, thin accent line on the edge.
5. Start the first motion in a new shot 0.1–0.3 s after the cut; after an important element lands, hold the frame ≥ 1 s.

```js
// dissolve into the end card
tl.fromTo("#endcard", { opacity: 0 }, { opacity: 1, duration: 1.0, ease: "power1.inOut" }, tEnd - 1.0);
// clip-path wipe left to right
tl.fromTo("#sceneB", { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: 1.1, ease: "power2.inOut" }, tCut);
```

## Verify
Count transitions in the timeline: at most three showy ones, the rest hard cuts.

## Don't
Don't apply this to a video that teaches transitions themselves.

## Evidence
No own measurements; values from a camera-moves reference. In analysed hits cuts are hard, one every 1.6–2.3 s.

## Related
- [Whip pan with motion blur](transitions-whip-pan.md)
- [Smash cut](transitions-smash-cut.md)
- [Skit cut rhythm](transitions-skit-cut-rhythm.md)
- Example: [TV ads switched off](../../examples/tv-no-ads/README.md)
