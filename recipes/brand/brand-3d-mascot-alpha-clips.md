---
id: brand-3d-mascot-alpha-clips
title: Make a 3D mascot read as its species from the silhouette, then render reusable alpha clips per emotion
section: brand
lang: any
status: hypothesis
evidence: viewer-feedback
tools: [Blender, ffmpeg]
learn: ../../learn/en/04-image-and-frame.md
added: 2026-10-28
updated: 2026-10-29
contributors: [not-a-blogger]
---

## When
A channel mascot moves from a flat picture to 3D (code primitives, a sculpt, a toy-like render). Viewers say it looks like a different animal, it shows one face for the whole video, and every new video re-renders it from scratch.

## Do
1. List the 3–4 traits that tell the species apart from its look-alikes and build them first, before colour and detail. For a gorilla vs a bear: a sagittal crest on top of the head, a heavy brow ridge, a flat wide nose, a hump of trapezius muscles. Check the silhouette in black: it must read without the face.
2. Give the mascot a small set of named poses (shock, wow, wink, point, stop, shrug…) and switch the pose on every meaning block of the script, not once per video.
3. Keep "always alive" channels on top: breathing, a slow sway, blinks, nods on list items.
4. Render each pose once as a short clip with alpha (2–3 s) in two formats: ProRes 4444 for editing, VP9 WebM with alpha for the browser engine. Reuse the clips in later videos instead of re-rendering.
5. Check hand poses on stills before the full render, see [frame review](../qa/qa-dry-frame-review.md).

```bash
ffmpeg -framerate 30 -i frames/%04d.png -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le point.mov
ffmpeg -framerate 30 -i frames/%04d.png -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 30 point.webm
```

## Verify
- A person who doesn't know the channel names the animal from a black silhouette.
- The timeline has a pose change on every meaning block; no pose stays longer than one block.
- ProRes: `ffprobe` shows `pix_fmt=yuva444p10le`. VP9 WebM: `ffprobe` reports `pix_fmt=yuv420p` even when alpha is there (alpha sits in a side channel), so check the `alpha_mode=1` tag and decode the alpha with the `libvpx-vp9` decoder: the alpha plane must hold both transparent (YMIN 0) and opaque (YMAX 255) pixels.
- Composite one frame over a contrasting colour and look at it: the mascot sits on magenta with clean edges, no black box.

```bash
ffprobe -v error -select_streams v:0 -show_entries stream_tags=alpha_mode -of default=nw=1 point.webm   # TAG:alpha_mode=1
ffmpeg -v error -c:v libvpx-vp9 -i point.webm -vf "alphaextract,signalstats,metadata=print:file=-" -frames:v 1 -f null - \
  | grep -E "signalstats.Y(MIN|MAX)="                                                                  # YMIN=0, YMAX=255
ffmpeg -v error -y -f lavfi -i color=magenta:s=1080x1920 -c:v libvpx-vp9 -i point.webm \
  -filter_complex "[0][1]overlay=shortest=1" -frames:v 1 check.png
```

## Don't
- Don't use someone else's mascot, logo or palette (see [BRAND.md](../../docs/BRAND.md)); build your own.
- Don't add detail before the species reads: fur and colour don't fix a bear-shaped skull.

## Evidence
- A three.js mascot built from primitives without the species traits got "looks like a bear" from the author; the next version added the traits.
- A sculpted vinyl-toy version with a crest, brow ridge, flat nose and trapezius hump, 14 poses switched per block, five 2.6 s alpha clips (ProRes 4444 + VP9) was built 28 Oct 2026; not yet reviewed or published, hence hypothesis.

## Related
- [Mascot once per episode, logo last](brand-mascot-once-logo-last.md)
- [Stickers outside the camera](brand-stickers-outside-camera.md)
- [Frame review before render](../qa/qa-dry-frame-review.md)
