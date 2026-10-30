---
id: voice-loudness-per-take
title: Normalise every take to −16 LUFS before mixing
section: voice
lang: any
status: proven
evidence: measurement
tools: [ffmpeg]
learn: ../../learn/en/03-voice.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Takes differ in loudness (a calm reference synthesizes much quieter than an emotional one); the voice drowns under music and ASR errs.

## Do
Normalise each take before mixing with music, not the whole mix at the end. Target −16 LUFS, TP −2: the value the blind test was measured at ([QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md)).

```bash
for f in voice-*.wav; do
  ffmpeg -y -i "$f" -af "loudnorm=I=-16:TP=-2" -ar 44100 "norm/${f}"
done
```

## Verify
`ffmpeg -i norm/voice-3.wav -af ebur128 -f null -` shows Integrated ≈ −16 LUFS for every take; no line sinks under the music in the mix.
All takes at once: `python3 tools/qa/loudness.py --target take norm/*.wav` (exit 1 on a take outside −17…−15 LUFS or above TP −2).

## Don't
Don't expect short lines to hit the target exactly with a TP −2 ceiling.

## Evidence
- Calm reference synthesized about 13 dB quieter than the emotional one.
- Blind test at target −16 LUFS, TP −2: lines came out at −16.0…−16.9. An earlier version of this recipe said −18; that value was never measured and is now only the starter's pre-mix bus level.

## Related
- [Final loudness like hits](../sound/sound-loudness-like-hits.md)
- [Gaps between lines](voice-gaps-between-lines.md)
- Example: [Guess which voice is mine](../../examples/guess-my-voice/README.md)
