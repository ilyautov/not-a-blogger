---
id: assembly-content-proportion
title: Lay out blocks to the frame's proportion instead of relying on camera zoom
section: assembly
lang: any
status: proven
evidence: measurement
tools: [CSS, GSAP]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A two-line quote (1440×170 block) or a chain of four pills in a row (1300×90) is "wide" while three quarters of the 16:9 frame stay empty. No zoom fits such a strip.

## Do
1. Narrow a quote to 1080 px and raise font size to 84+ so it runs 3–4 lines.
2. Spread steps over the safe zone with a step cap `(780 − 170) / (n − 1)`, or the last one overflows.
3. Put a 3–4 link chain in two columns; center an incomplete row.
4. Make lists and comparisons filled cards: filled area counts as fill, thin text doesn't.

```css
.quote { width: 1080px; font-size: 84px; line-height: 1.08; }
.chain { display: grid; grid-template-columns: repeat(2, 560px); gap: 40px; justify-content: center; }
.step  { background: #fff; border-radius: 12px; padding: 28px 36px; }
```

## Verify
Grid fill measured on the rendered mp4, broken down by scene type.

## Don't
Don't reuse horizontal blocks as-is for vertical; re-layout them (see vertical recipes).

## Evidence
- Fill by scene type (96 scenes): terminal 70–76%, quote 43%, file 35%, steps 31%, comparison 27%, chain and lanes ~21%.
- One editing pass: median 25% → 32%, scenes below 20%: 21 → 10, empty time 19% → 8%.

## Related
- [Camera follows ink](../camera/camera-follow-ink.md)
- [Terminal typing](assembly-terminal-typing.md)
- [Frame fill on the mp4](../qa/qa-frame-fill-mp4.md)
