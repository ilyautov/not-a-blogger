---
id: face-ltx-a2v-local
title: Make a talking character locally with LTX audio-to-video
section: face
lang: any
status: proven
evidence: measurement
tools: [LTX-2, ltx-2-mlx, ffmpeg]
learn: ../../learn/en/04-image-and-frame.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
You need a talking person or mascot in frame; photo lip-sync looks jittery and cloud services cost money.

## Do
1. One frame (photo or a frame of your own video) + the line's wav → a2v mode of a local video model.
2. Split lines into 4–5 s chunks; generate each separately; concatenate.
3. Pad the wav with silence to the clip length (shorter wav → generation fails).
4. Put the chunks with the most stable face at the start of the shot: the face drifts toward mid-clip.

```bash
ffmpeg -y -i line.wav -af "apad=whole_dur=5" line5.wav
# then: a2v with face.png and line5.wav, 576×1024, ~5 s
```

## Verify
Clip contact sheet: face recognisable at start and end, mouth in sync with sound.

## Don't
- Don't make long chunks: the face drifts mid-clip.
- Generate only your own face or one with consent; never real third parties.
- LTX is a gated model with its own license; newer versions require a Hugging Face login.

## Evidence
- Apple M1 Max, LTX-2.3 q8 distilled: 4–5 s clip at 576×1024 in 262–287 s; mascot a2v 4 s in 153 s; peak memory ~27 GB.
- 34 s video: 8 chunks, 31 min compute; 131 s video: 22 chunks, 74 min.
- Author's rating: a2v is livelier than mouth-only lip-sync (facial expression, head motion).

## Related
- [Lip-sync over your own video](face-musetalk-real-video.md)
- [Don't generate real people](face-no-real-person.md)
- [Generative insert between stills](../image/image-ai-insert-between-frames.md)
- Prompt: [film-look shot in two steps](../../prompts/video-gen/film-look-reference-frame.md)
