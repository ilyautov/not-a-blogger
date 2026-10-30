---
id: image-depth-parallax-layers
title: Split an image into layers by depth map and move them at different speeds
section: image
lang: any
status: hypothesis
evidence: experience
tools: [Depth-Anything-V2-Small, OpenCV, GSAP, tools/image/depth_layers.py]
learn: ../../learn/en/04-image-and-frame.md
added: 2026-10-23
updated: 2026-10-29
contributors: [not-a-blogger]
---

## When
A slow push-in on a flat image (Ken Burns) reads as static, and two-copy pseudo-parallax fails (`clip-path` seams, gradient masks double edges).

## Do
1. Compute a depth map locally (Depth-Anything-V2-Small, ~95 MB, offline).
2. Cut the image into 4 layers by depth thresholds with `tools/image/depth_layers.py`. Build every layer from the original image, inpainting only what nearer layers cover, and keep the far layer fully opaque; chaining inpaints from one layer to the next destroys near objects and leaves holes in the back plate.
3. Masks are cleaned with morphology (close + open), or layers break into blotches.
4. Move each layer at its own speed and scale.

```bash
pip install opencv-python-headless numpy torch transformers pillow
python3 tools/image/depth.py art.jpg --download              # first run fetches Depth-Anything-V2-Small (Apache-2.0)
                                                             # writes art.depth.png (0 far, 255 near)
# already have a depth map from elsewhere? save it as art.depth.png and skip depth.py
python3 tools/image/depth_layers.py art.jpg --cuts 55 105 175 --out-dir build/layers
# → build/layers/art.L0.png … art.L3.png; L0 is an opaque back plate,
#   each layer is cut from the original image with the nearer layers inpainted away
```

```js
// far layer ~60 px per shot, near layer ~190
tl.to("#L0", { x: -60,  duration: 6, ease: "none" }, 0)
  .to("#L3", { x: -190, scale: 1.04, duration: 6, ease: "none" }, 0);
```

## Verify
On the contact sheet layers separate with no inpaint traces at the edges; the stillness lint does not flag the scene.

## Don't
- Don't exceed ~60 px (far) / ~190 px (near): inpaint traces show at the edges.
- License: Depth-Anything-V2-Small is Apache-2.0; Base and Large weights are CC BY-NC. Check the model card before use.

## Evidence
- Push-in on a flat frame at 0.6 % per second was rejected as "not enough dynamics".
- Layer travel: up to ~60 px far and ~190 px near; beyond that inpaint traces appear.
Pixel limits were tuned by eye on a few frames; no viewer or retention measurement of the four-layer parallax against a flat push-in. To promote: an A/B of the same frame with layers and without, judged by the approver or by retention of a published pair.

## Related
- [Parallax by depth formula](../camera/camera-parallax-formula.md)
- [No Ken Burns](../camera/camera-no-ken-burns.md)
