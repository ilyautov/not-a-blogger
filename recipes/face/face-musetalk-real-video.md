---
id: face-musetalk-real-video
title: Replace only the mouth over real video instead of animating a photo
section: face
lang: any
status: proven
evidence: measurement
tools: [MuseTalk, ffmpeg]
learn: ../../learn/en/04-image-and-frame.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A talking head from one photo (SadTalker and similar) looks jittery, and your own on-camera video lacks usable audio.

## Do
1. Take real video of the person (a selfie talking or just looking into the camera).
2. Apply the new audio with a lip-sync model that changes only the mouth region (MuseTalk v1.5); the rest stays live video.
3. If the source audio is audible only in places, use those parts as a voice reference or record a new voice-over.

```bash
# where the source has speech
ffmpeg -i source.mov -af "silencedetect=n=-40dB:d=1" -f null - 2>&1 | grep silence_
```

## Verify
The mouth looks natural in close-up; no head jerks on the contact sheet.

## Don't
- Don't animate a single photo and then lip-sync it.
- Don't expect the picture to save a bad voice: the voice was the bottleneck.
- Check MuseTalk weight licenses before commercial use.

## Evidence
- 19 s of video processes in about 2.5 min on Apple Silicon (MPS).
- Mouth natural; moustache smeared.
- The earlier "jittery avatar" verdict applied to "photo animation + lip-sync", not lip-sync over video.
- Six synthesis variants for the same head were rejected.

## Related
- [Talking character via LTX](face-ltx-a2v-local.md)
- [Live voice for the character](../voice/voice-live-for-character.md)
