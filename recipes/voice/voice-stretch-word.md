---
id: voice-stretch-word
title: Stretch a word with formant-preserving rubberband, not by spelling
section: voice
lang: any
status: proven
evidence: ab-test
tools: [rubberband, ffmpeg, WhisperX]
learn: ../../learn/en/03-voice.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
You need a long, juicy shout and the TTS won't stretch the word. Caps and repeated letters barely help; `atempo 0.5` sounds distorted.

## Do
1. Cut the word from the finished take by ASR timestamps.
2. Split off the final consonant(s); don't stretch them.
3. Stretch the rest ×2 with formant preservation.
4. Rejoin with a 10 ms crossfade and normalise.

```bash
rubberband-r3 -q --fine --formant -t 2 word_body.wav word_body_x2.wav
ffmpeg -y -i word_body_x2.wav -i word_end.wav \
  -filter_complex "[0][1]acrossfade=d=0.01,loudnorm=TP=-2" word_stretched.wav
```

## Verify
Blind choice between ×2 and ×2.5 stretches; ASR still recognises the word.

## Don't
- Don't stretch beyond ×2.
- Profanity in the hook cuts reach on platforms; that is an editorial decision, not a technical one.

## Evidence
- Spelling alone grew the word only from 0.5 to 0.68 s.
- A/B: ×2 won, ×2.5 sounded worse.

## Related
- [Stress by rewording](voice-stress-by-rewording.md)
- [Don't speed up the clone](voice-no-speedup-clone.md)
