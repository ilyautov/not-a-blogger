---
id: camera-no-ken-burns
title: Don't mask a static frame with a slow push-in
section: camera
lang: any
status: proven
evidence: measurement
tools: [GSAP]
learn: ../../learn/en/05-camera-editing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A card hangs in frame with nothing happening inside, and a slow push-in over the whole scene is added. The frame technically moves; the viewer sees a slide. Stillness metrics are fooled too.

## Do
1. Put motion inside the frame: text appears line by line at speech pace, a terminal types, a list reveals item per word, a page scrolls to the paragraph.
2. Change shot scale with a pan (see related recipe), not a few-percent zoom.
3. Disable the global camera push-in before measuring stillness.

```js
// before the stillness lint: zero the camera
gsap.set("#world", { clearProps: "transform" });
```

## Verify
Run the stillness lint with the camera off: the count of static scenes does not depend on whether the push-in is on.

## Don't
Don't let a drift be the only motion in a shot. A slow drift is fine only when there is action inside the frame.

## Evidence
- With a slow push-in over the whole scene the stillness lint reported 3 static scenes; without it, 41.
- A 1.0 → 1.06 push-in over 5 s on a 20-minute video got "illustrations are static".
- A 0.6%/s push-in on a single image: "not enough dynamics".

## Related
- [Change shot scale instead of zoom](camera-scale-change-not-zoom.md)
- [Stillness lint](../qa/qa-still-lint.md)
- [Terminal typing](../assembly/assembly-terminal-typing.md)
- Example: [Whole course in 20 minutes (failed)](../../examples/course-retelling/README.md)
