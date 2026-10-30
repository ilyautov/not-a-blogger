# Image and backgrounds

Photos, parallax, generative inserts, maps. Recipes follow the [template](../../templates/recipe.md).

| Recipe | Status | Lang | Gist |
|---|---|---|---|
| [Insert 2–3 s of generative video between two stills](image-ai-insert-between-frames.md) | hypothesis | any | i2v clamped between scene stills, JSON prompt, take selection. |
| [Own photo background per chapter, generated in parallel](image-chapter-backgrounds-parallel.md) | proven | any | Four in 80 s; frame fill 78 % vs 24 %. |
| [Depth-map layers moving at different speeds](image-depth-parallax-layers.md) | hypothesis | any | Depth map → 4 inpainted layers; ~60 px far, ~190 px near. |
| [3D map flyover rendered frame by frame](image-map-flyover.md) | proven | any | MapLibre + terrain, wait for idle, ~0.13 s per frame. |
| [Real object, real photo](image-real-object-real-photo.md) | hypothesis | any | Free-license photo instead of a drawn silhouette. |
| [Period footage and music from archive.org](image-archive-footage-prelinger.md) | hypothesis | any | Prelinger / 78rpm via archive.org API; licenseurl per item, attribution in the description. |
| [Seamless background loop](image-seamless-loop-bg.md) | hypothesis | any | First second = tail-to-head crossfade; seam.py: seam ≤ 2 × median neighbour diff. |
