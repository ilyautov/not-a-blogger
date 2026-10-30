---
id: vertical-titles-on-joint
title: Put vertical titles on the scene joint and space lines at least 0.75 s apart
section: vertical
lang: any
status: proven
evidence: measurement
tools: [GSAP, Python]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
In a short built from a long video, scene number and title appear on the narrator's word; every scene change shows empty background. The long video's pauses are too short for a joint.

## Do
1. Number and title arrive on the scene joint, not on a word.
2. Space lines at least 0.75 s apart to leave room for the change.
3. In a shared `fade_in`, end values are 0 for offsets and 1 for scale. A single `:0` for all properties sends cards to `scale:0` and they never appear.
4. On dark ground the header is light from frame zero.
5. Compute music ducking and swells from the short's end of speech; don't copy them from the long.

```python
GAP_MIN = 0.75
for i in range(1, len(lines)):
    gap = lines[i]["start"] - lines[i-1]["end"]
    if gap < GAP_MIN:
        shift = GAP_MIN - gap
        for l in lines[i:]:
            l["start"] += shift; l["end"] += shift
```

```js
const FADE_END = { x: 0, y: 0, scale: 1, autoAlpha: 1 };   // scale 1, not 0
```

## Verify
Contact sheet: no empty background at joints; cards visible at every joint.

## Don't
Don't space lines in a short that runs as one continuous stream without scene changes.

## Evidence
- Word-anchored titles left 0.8 s of empty background between scenes, five times in a 45 s video.
- Long-video pauses of 0.02–0.3 s are too short for a joint.
- Olive title on dark background gave 1.99:1 contrast.

## Related
- [Empty scene start](../assembly/assembly-no-empty-scene-start.md)
- [Re-layout, not crop](vertical-relayout-not-crop.md)
