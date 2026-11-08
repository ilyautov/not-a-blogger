---
id: vertical-platform-ui-zones
title: Keep captions and the call to action out of the platform UI zones in vertical video
section: vertical
lang: any
status: hypothesis
evidence: experience
tools: [ffmpeg]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-11-08
updated: 2026-11-08
contributors: [not-a-blogger]
---

## When
In the Reels, Shorts or TikTok player, captions, numbers or the call to action end up under the like and share column,
the author line, the description or the progress bar. In the editor the frame looked fine.

## Do
1. Keep captions at least 330 px above the bottom edge of a 1080×1920 frame, and leave the bottom ~300 px for the
   description and navigation.
2. Keep key text and numbers in the central area: away from the right edge, where the button column sits.
3. Build the mask from your own screenshot, not from someone's template: publish privately (or open a draft), take a
   phone screenshot of the player on each platform, scale it to 1080×1920 and keep it next to the project.
4. Overlay the mask on the key frames (hook, numbers, final call to action) before publishing.

```bash
# quick check: shade the bottom 330 px on a key frame
ffmpeg -ss 1.5 -i output/final.mp4 -frames:v 1 \
  -vf "drawbox=x=0:y=ih-330:w=iw:h=330:color=red@0.35:t=fill" qa/ui-zone-bottom.png

# full check: overlay a platform screenshot scaled to the frame
ffmpeg -ss 1.5 -i output/final.mp4 -i qa/ui-reels.png -frames:v 1 \
  -filter_complex "[1]scale=1080:1920,format=rgba,colorchannelmixer=aa=0.5[m];[0][m]overlay" qa/ui-reels-check.png
```

## Verify
On every key frame with the mask on, no caption letter, number or link in the call to action is covered.

## Don't
- Don't fix this by shrinking everything: move the text, keep its size
  ([re-layout, not crop](vertical-relayout-not-crop.md)).
- Don't reuse one platform's mask for another: the button column and description sit at different heights.
- Don't treat ad-placement safe zones from platform ad guides as numbers for organic posts: they describe a different
  player layout.

## Evidence
- Captions at 330 px from the bottom were used in the 3D-skit styles; the bottom ~300 px were left free in a vertical
  explainer (captions at y≈1475–1610, subject up to 1380). No caption was reported covered on those published videos.
- Not measured: the exact width of the right button column per platform. To promote: overlay screenshots from three
  platforms on N published videos and count covered elements with and without the rule.

## Related
- [Compute the camera shot so the hero never leaves the frame](../camera/camera-keep-in-frame.md)
- [Vertical titles on the scene joint](vertical-titles-on-joint.md)
