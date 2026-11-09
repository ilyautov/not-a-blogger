---
id: assembly-motion-vocabulary-numbers
title: Describe drawn and Swiss motion moves in frames and percent, not in adjectives
section: assembly
lang: any
status: hypothesis
evidence: experience
tools: [GSAP]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-11-09
updated: 2026-11-09
contributors: [not-a-blogger]
---

## When
A brief or a prompt says "bouncy", "snappy", "hand-drawn feel", and the agent animates everything with one fade and
one ease. You want a drawn or Swiss motion-design look and need moves the agent can execute exactly.

## Do
Write each move as numbers. Starting values (at 30 fps; recompute frames for 60):

| Move | How much | GSAP sketch |
|---|---|---|
| Smear frame | one in-between frame of a fast move stretched 150–300 % along the motion, exactly 1 frame | `tl.set(el,{scaleX:2.2,transformOrigin:'0 50%'},t).set(el,{scaleX:1},t+1/FPS)` |
| Line boil | 3–4 outline variants offset 2–5 px, switch every 2 frames | variant = `Math.floor(frame/2)%3`; no `Math.random()`; drawn styles only |
| Pop with overshoot | scale 0 → 1.15 → 1.0 over ~8 frames; per letter with a 2-frame stagger | `keyframes:{scale:[0,1.15,1]}, duration:8/FPS, stagger:2/FPS` |
| Knife delete | a thin line crosses the element, then it collapses to its midline; no fades | line `scaleX 0→1` 4–6 frames `none`, then `scaleY 1→0` 6–8 frames `cubic-bezier(.7,0,.2,1)` |
| Rise from the baseline | a word rises out of a mask by 0.6–1.0 line height, leaves upward | wrapper `overflow:hidden` with room for accents and descenders; `yPercent:100→0`, `expo.out` 0.2–0.33 s |
| Colour-plate wipe | a scene or background change goes through a plate of colour | `cubic-bezier(.7,0,.3,1)`, 3 frames of cushion at both ends |

1. Pick 2–3 moves that fit the style; don't use all six in one video.
2. Put the numbers into the scene code and into the series `STYLE.md`, so the next episode uses the same values.
3. A reaction caption lands 2–3 frames after its event; the key word of a punchline line leads the sound by ~0.2 s.

## Verify
Step through the moves frame by frame (`window.setTime(t)` or an exported frame strip): the smear lasts exactly one
frame, the overshoot peaks at 1.15, the knife delete has no opacity change. The motion lint passes.

## Don't
- Don't hold a smear for two or more frames: at 30 fps that reads as a glitch.
- Don't use `Math.random()` for boil: frames must be a function of time.
- Don't apply drawn moves (smear, boil) to a clean UI or a 3D scene; they belong to drawn styles.

## Evidence
No measurement on the author's videos. The numbers are retold from Vincentwei1021/mg-styles-15 (MIT): `template.md`
("style traits are written as numbers, not adjectives") and prompts for cel-boil, a three-layer reaction caption and
morph; knife delete and rise from the baseline from sarpstar/cinecode (MIT), `styles/swiss-motion.md` and
`references/typography.md`. The knife-delete frame counts are the author's starting values. To promote: rate videos
with and without these moves with the person, or measure retention.

## Related
- [Durations, easing and stagger from a table](assembly-motion-timing.md)
- [Anchor animation to word times](assembly-word-anchored-animation.md)
- [Frame = pure function of time](assembly-deterministic-timeline.md)
- [One shape, no cuts](../transitions/transitions-one-shape-no-cuts.md)
