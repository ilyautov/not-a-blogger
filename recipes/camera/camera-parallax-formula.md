---
id: camera-parallax-formula
title: Move 2D layers by the depth formula dx = camX / z
section: camera
lang: any
status: hypothesis
evidence: experience
tools: [Canvas 2D, GSAP]
learn: ../../learn/en/05-camera-editing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
In a 2D scene all layers shift equally and camera motion looks like sliding a flat picture.

## Do
1. Give each layer a depth `z`.
2. Screen shift `dx = camX / z`; push-in scale `s = f / (z − camZ)`. Near layers grow and separate faster.
3. Pan (camera rotation): move all layers by the same `dx`. Tracking shot: layers move at `v / z`, the hero stays.
4. Put at least one foreground object in frame; without it a push-in is indistinguishable from zoom.

```js
const layers = [{ el: "#far", z: 8 }, { el: "#mid", z: 3 }, { el: "#near", z: 1.2 }];
function camera(camX, camZ, f = 1) {
  for (const L of layers) {
    const s = f / (L.z - camZ);
    gsap.set(L.el, { x: -camX / L.z, scale: s });
  }
}
```

## Verify
On two frames with different `camX`, the near layer moved more than the far one by the ratio of their depths.

## Don't
Don't attempt a true orbit in 2D; at most spread layers apart and squeeze the hero horizontally.

## Evidence
No own measurements; formula from a camera-moves reference. For depth-map layers a travel of ~60 px (far) and ~190 px (near) is already verified.

## Related
- [Depth-map layers](../image/image-depth-parallax-layers.md)
- [Handheld camera](camera-handheld-sines.md)
