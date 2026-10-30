---
id: brand-stickers-outside-camera
title: Put stickers and the mascot in a layer outside the camera with a white four-shadow outline
section: brand
lang: any
status: hypothesis
evidence: experience
tools: [CSS, GSAP]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Brand stickers (mascot, badges, stamps) placed in the scene move with the camera: a push-in enlarges them, a pan takes them off screen. A cut-out PNG without an outline looks pasted on, not like a sticker.

## Do
1. Separate layer above the scene and outside the container the camera moves: the sticker is glued to the lens, not the world.
2. White outline from four `drop-shadow`s without blur.
3. Motion: enter `ease-out` (or `expo.out`), exit twice as fast as entry, start from `scale(.94)`, not zero, 30–80 ms stagger, animate only `transform` and `opacity`.
4. An element hanging from a dark card onto a light background must read on both: white backing, dark text.

```html
<div id="world"> ... scene, moved by the camera ... </div>
<div id="stickers"><img class="sticker" src="mascot.png"></div>
```

```css
#stickers { position: absolute; inset: 0; pointer-events: none; }
.sticker {
  filter: drop-shadow( 3px 0 0 #fff) drop-shadow(-3px 0 0 #fff)
          drop-shadow(0  3px 0 #fff) drop-shadow(0 -3px 0 #fff);
}
```

```js
gsap.fromTo('.sticker', { opacity: 0, scale: .94 }, { opacity: 1, scale: 1, duration: .4, ease: 'expo.out' });
gsap.to('.sticker', { opacity: 0, duration: .2, ease: 'power2.in', delay: 2.6 });
```

## Verify
On push-in frames the sticker keeps size and position; the outline is visible along the whole contour.

## Don't
- Don't lift in-world stickers (a sticker on a laptop in frame) out of the scene: the camera legitimately moves them.

## Evidence
No own measurement.

## Related
- [Mascot once per episode, logo at the end](brand-mascot-once-logo-last.md)
- [Sticker pack in code](../carousels/carousels-stickers-text-by-code.md)
- Example: [A hook that blocks a dangerous command](../../examples/hook-vertical-from-long/README.md)
