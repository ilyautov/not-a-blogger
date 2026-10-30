---
id: image-ai-insert-between-frames
title: Insert 2–3 s of generative video between two still frames of your own scene
section: image
lang: any
status: hypothesis
evidence: experience
tools: [LTX-2, ltx-2-mlx, ffmpeg]
learn: ../../learn/en/04-image-and-frame.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The video needs "live" shots, but an all-generative video drifts (faces change, hands break, dozens of takes).

## Do
1. Make each insert 2–3 s, clamped between two stills of the HTML scene: the i2v first and last frames equal the scene frames; the model invents only the motion.
2. Cut on action; drop the middle with melting hands. Add your own grain and titles on top.
3. Structure the prompt as JSON. Keep subject, style, lighting identical across takes; vary only action and camera. Paste the character description verbatim into every prompt.
4. 3–4 takes per insert, then select: give a VLM judge the candidates, the prompt, and the previous clip; prefer a pairwise tournament over absolute scores.
5. Justify low image quality with a genre: CCTV, home camera, VHS, with a "reconstruction" label.
6. Pad short audio for a2v/i2v to the clip length.

```json
{"subject": "<verbatim character passport>", "action": "looks at the robot and stops",
 "scene": "night street, sidewalk", "camera": "static CCTV high angle", "lens": "wide",
 "lighting": "street lamps", "style": "surveillance footage, grain",
 "audio": "none", "negative": "no subtitles, no captions, no text overlays"}
```

```bash
ffmpeg -y -i line.wav -af "apad=whole_dur=4" line_pad.wav
```

## Verify
The seam with the scene is invisible on the contact sheet; the log records "generations per usable shot".

## Don't
- Don't generate real people realistically; platforms require an AI label for such content.
- Don't ask for cuts inside one generated clip (unstable): generate two shots and cut in the edit.
- Don't feed a2v a wav shorter than the frame count: it fails; pad with `apad`.
- LTX-2.x is a gated model with its own license: read the terms before using it in a video.

## Evidence
- Local LTX-2.3 q8 distilled on Apple M1 Max, 4 s clip: t2v 576×1024 in 223 s, i2v 512×768 in 151 s, a2v in 153 s; peak memory ~27 GB.
- Cloud via an aggregator: ~$0.06 per second of B-roll with a cheap model, ~$4–8 per short.
- External yield reference: an ad from 300–400 generations gave 15 clips (~4–5 %).

## Related
- [Talking head on LTX](../face/face-ltx-a2v-local.md)
- [Don't generate real people](../face/face-no-real-person.md)
