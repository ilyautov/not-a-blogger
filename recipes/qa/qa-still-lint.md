---
id: qa-still-lint
title: Catch frame stillness from the timeline with the camera off
section: qa
lang: any
status: proven
evidence: measurement
tools: [Playwright, GSAP, Python]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The motion lint (easing, durations) checks animation code, not the result. A frame can stay unchanged for 6 s and nobody sees it before the viewer.

## Do
1. Seek the timeline in 1.5 s steps and count consecutive seconds without change. A scene fails when the frame stands longer than 3 s ([QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md)); `tools/lint/still_lint.py --max-still 3` does this on real frames.
2. Kill the global camera push-in before capture: zooming a dead card is not motion.
3. Run the lint only with word-level timestamps: without them all anchors fall on line starts, elements clump, and the result is meaninglessly pessimistic.
4. Stillness and fill are different diseases; run both checks.

```js
// inside the scene page
async function stills(tl, step = 1.5) {
  gsap.set("#world", { clearProps: "transform" });       // zero the camera
  const out = []; let prev = null;
  for (let t = 0; t < tl.duration(); t += step) {
    tl.seek(t, false); await new Promise(r => requestAnimationFrame(r));
    const sig = [...document.querySelectorAll("#scene *")].map(e => getComputedStyle(e).opacity + getComputedStyle(e).transform).join("|");
    out.push({ t, same: sig === prev }); prev = sig;
  }
  return out;                                             // consecutive same → stillness
}
```

## Verify
No run of `same` longer than 3 s; a technique that lights items one by one yields single-digit stillness percentages.

## Don't
Don't use this lint to find empty frames with changing captions; use mp4 frame fill for that.

## Evidence
- With push-in on the lint reported 3 static scenes, with it off 41.
- Without word timestamps there was a ~6.5 s hole between events.
- Items lighting up one by one: 6% stillness.

## Related
- [Frame fill on the mp4](qa-frame-fill-mp4.md)
- [No Ken Burns](../camera/camera-no-ken-burns.md)
- Example: [Whole course in 20 minutes (failed)](../../examples/course-retelling/README.md)
