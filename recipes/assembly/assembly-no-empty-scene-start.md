---
id: assembly-no-empty-scene-start
title: Bring the scene block in at the cut and light up rows on their words
section: assembly
lang: any
status: proven
evidence: measurement
tools: [GSAP, ffmpeg]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A list, menu or big number is anchored to the word that names it. The line starts with a lead-in, the word arrives at second 4–5, and until then the frame is empty background with captions. Audio and timing checks are green.

## Do
1. The scene block appears at the cut: `t_scene + 0.35`.
2. Rows inside stay dimmed (`opacity .24–.3`) and each lights up on its word.
3. If the first item's word is more than 2 s into the scene, the first item appears no later than `t_in + 0.45`.
4. Never show an empty card before its first row: move the whole card forward, not just the frame.

```js
tl.fromTo(".list", { autoAlpha: 0, y: 24 }, { autoAlpha: 1, y: 0, duration: 0.35 }, tScene + 0.35);
tl.set(".list li", { opacity: 0.27 }, tScene + 0.35);
items.forEach((li, i) => tl.to(li, { opacity: 1, duration: 0.2 }, W(cue, li.dataset.word)));
```

## Verify
Contact sheet `ffmpeg -i final.mp4 -vf "fps=1/2,scale=320:-1,tile=6x2" sheet_%02d.jpg` plus grid fill on the mp4: no consecutive empty frames at scene starts.

## Don't
Don't expect this to help a line with no picture at all: it needs content.

## Evidence
- Median frame fill rose from 23% to 33–43% on four shorts.
- Before the fix contact sheets showed three consecutive empty frames per scene.
- On a 27-minute video 22% of runtime was empty background with green checks.

## Related
- [Word-anchored animation](assembly-word-anchored-animation.md)
- [Frame fill on the mp4](../qa/qa-frame-fill-mp4.md)
- [Voice by 0.45 s](../hooks/hooks-voice-by-045.md)
