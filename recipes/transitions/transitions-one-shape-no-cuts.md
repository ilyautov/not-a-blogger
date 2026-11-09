---
id: transitions-one-shape-no-cuts
title: Build an interface loop or how-to as one shape that morphs, with no cuts and a cursor that drives the story
section: transitions
lang: any
status: hypothesis
evidence: experience
tools: [GSAP]
learn: ../../learn/en/05-camera-editing.md
added: 2026-11-09
updated: 2026-11-09
contributors: [not-a-blogger]
---

## When
A product loop, a how-to or a pure motion piece turns into a slideshow: a new card on every beat, a cut between
every state. Not for skits with characters, where cuts stay.

## Do
1. **One shape.** Every state is the same element changing size, radius and colour. Content inside it swaps with a
   short blur of 4–6 frames.
2. **The next scene grows out of the previous one.** A gesture (click, drag, expand) carries the camera into the next
   world. Morph ≈ 0.8 s on `cubic-bezier(.45,0,.15,1)`, the camera zoom on the same curve, so the shape change is
   almost invisible. Old content dissolves in the second half of the morph.
3. **Text inside the morph** gets its own clip and timing: it enters after the morph starts and leaves before the
   next one starts. A tween shared with the container overlaps two captions.
4. **The cursor drives the story, the camera follows the state.** Every change starts with a visible click or drag;
   the camera frames the new state so it fills the frame, it does not chase the cursor. The cursor arrives before the
   camera.
5. **Loop seam.** For a loop, the last frame equals the first, including cursor position and speed and the phase of
   any drift.

```js
tl.to(shape,  {width: 880, height: 520, borderRadius: 28, duration: 0.8, ease: "cubic-bezier(.45,0,.15,1)"}, t)
  .to(camera, {scale: 1.12, duration: 0.8, ease: "cubic-bezier(.45,0,.15,1)"}, t)
  .to(oldText, {autoAlpha: 0, filter: "blur(6px)", duration: 0.2, ease: "power2.in"}, t + 0.4)
  .from(newText, {autoAlpha: 0, filter: "blur(6px)", duration: 0.2, ease: "power2.out"}, t + 0.55);
```

## Verify
Scene detection on the mp4 finds no cuts in the loop (`tools/qa/scene_gate.py` reports `cuts: 0`), the contact sheet
shows one shape in every frame, and for a loop `python3 tools/qa/seam.py output/final.mp4` passes.

## Don't
- Don't share one tween between the container and its text.
- Don't let the camera follow the cursor frame by frame; it frames the result.
- Don't force this onto a character skit: there cuts carry the jokes.

## Evidence
No measurement on the author's videos. Collected from common patterns in an open prompt collection
(yihui-dev/awesome-opus5-5-videos, MIT, "one shape, never cut" and neighbouring prompts) and the morph timings there;
the loop-seam check is the kit's own `seam.py`. To promote: build one loop this way and one with cuts on the same
material and compare the person's verdicts or retention.

## Related
- [Cut hard by default](transitions-hard-cut-default.md)
- [One zone in frame, no chrome](transitions-one-zone-no-chrome.md)
- [Motion moves in numbers](../assembly/assembly-motion-vocabulary-numbers.md)
