---
id: sound-keep-noise-whooshes
title: Keep noise whooshes on cuts even if viewers hear them as sniffing
section: sound
lang: any
status: proven
evidence: video-metric
tools: [numpy, ffmpeg]
learn: ../../learn/en/06-sound-captions.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Band-passed noise whooshes on cuts get described as "a vacuum cleaner" or "someone sniffing", and you want to remove them for clean sound.

## Do
1. Put a noise whoosh on cuts by default: moderate but audible, below the voice.
2. Use funny comment questions about the sound or topic as ideas for reply videos.

```bash
# whoosh: pink noise through a band-pass with an envelope
ffmpeg -f lavfi -i "anoisesrc=color=pink:d=0.35:a=0.6" \
 -af "bandpass=f=1800:w=1200,afade=t=in:d=0.12,afade=t=out:st=0.15:d=0.2" whoosh.wav
```

## Verify
Judge by comments, not by cleanliness: the sound became a reason to comment.

## Don't
- Don't push the whoosh above the voice.
- Don't assume it transfers to a serious video on a complex topic: there noise may irritate.

## Evidence
TV-without-ads video: 212k Instagram views in one evening; top comment "Who keeps sniffing there?" got 111 likes, another on the same topic 21. Worked as a recognisable gag on one video.

## Related
- [SFX by meaning](sound-sfx-by-meaning.md)
- [Loudness like hits](sound-loudness-like-hits.md)
- Example: [TV ads switched off](../../examples/tv-no-ads/README.md)
- Example: [Guess which voice is mine](../../examples/guess-my-voice/README.md)
