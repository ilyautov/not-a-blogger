---
id: image-map-flyover
title: Render a 3D map flyover frame by frame in a headless browser
section: image
lang: any
status: proven
evidence: measurement
tools: [MapLibre GL JS, AWS Terrain Tiles, headless Chrome]
learn: ../../learn/en/04-image-and-frame.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A place-based topic (geolocation, city, route) needs a live flyover over terrain; screen recording stutters and tiles load mid-frame.

## Do
1. MapLibre GL JS + terrain from open elevation tiles (Terrarium); contours and ridge line from the same terrain.
2. Render frame by frame: set the camera for time `t`, wait for `idle` (all tiles loaded), capture. This makes the render deterministic.
3. Headless Chrome with GPU; join frames with ffmpeg.
4. Put tile-source attribution in frame.

```js
async function frame(t) {
  map.jumpTo(cameraAt(t));            // center, zoom, pitch, bearing from time
  await new Promise(r => map.once("idle", r));
  return map.getCanvas().toDataURL("image/png");
}
```

```bash
ffmpeg -framerate 30 -i frames/%05d.png -c:v libx264 -pix_fmt yuv420p flyover.mp4
```

## Verify
No frame has unloaded tiles; two renders of one timeline match.

## Don't
- Don't use Esri World Imagery satellite: it is under a Master License, no video rights without an ArcGIS account. Clean alternatives: NASA Blue Marble (public domain), EOxCloudless (CC BY-NC-SA, blurrier, 10 m/px).
- AWS Terrain Tiles are open but require attribution; OSM data is ODbL.

## Evidence
About 0.13 s per frame; probes of 8 s (mountains) and 3.5 s (globe between two cities) with no keys or accounts.

## Related
- [Chapter backgrounds in parallel](image-chapter-backgrounds-parallel.md)
- [Camera follows content](../camera/camera-follow-ink.md)
- Example: [Agent finds a place from a photo, tested blind](../../examples/photo-geo-blind-test/README.md)
