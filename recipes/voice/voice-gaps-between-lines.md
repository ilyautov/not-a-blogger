---
id: voice-gaps-between-lines
title: Take gaps between lines from the script, short and uneven, and fit the scene mechanics to speech
section: voice
lang: any
status: proven
evidence: measurement
tools: [ffmpeg, ebur128]
learn: ../../learn/en/03-voice.md
added: 2026-10-23
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
The timeline is laid out for the animation and gaps of 1.3–3.8 s appear between short lines. Or the opposite: every gap is the same constant, and the voice ticks like a metronome.

## Do
1. Write a gap for every joint in the script, by meaning: 0.2–0.5 s inside a thought, 0.5–0.8 s between thoughts, 0.6–0.9 s before the punchline (one hit used 1.1 s). Fit scene mechanics to speech, not speech to mechanics.
2. Add a random jitter of ±0.08 s to every gap, with a fixed seed so the build stays reproducible.
3. Keep gaps under 1 s except the one before the punch.
4. If a gap is extended for a background change, fill it with an event in frame, not air.

```python
import random
rng = random.Random(42)                       # fixed seed: same build, same gaps
# gaps[i] = pause after line i, written in the script by meaning (0.2–0.9 s)
t = 0.0
for dur, gap in zip(take_durations, gaps + [0.0]):
    starts.append(t)
    t += dur + max(0.12, gap + rng.uniform(-0.08, 0.08))
```

## Verify
- Measure pauses by RMS (0.5 s window) or silence below −35 dB, or with `tools/qa/voice_qa.py`: every gap except one is shorter than 1 s.
- Standard deviation of the gaps ≥ 0.1 s ([QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md)). Below that the rhythm is a metronome.

## Don't
- Don't use one constant `GAP` for all joints: that is exactly the metronome the check catches.
- Don't apply the same gaps to a voice with no internal pauses (meme reference): it needs more room.

## Evidence
- Gaps of 1.3 / 3.8 / 1.5 s set by mechanics were rejected as "very long pauses".
- Voxel skit with 710k views: one 1.1 s gap before the punch, all others 0.1–0.46 s.
- Seven analysed hits: no silence below −35 dB longer than 0.25 s, except one video without speech.
- Meme-reference probe: gaps raised from 0.55 to 0.9 s for a background change.
- Voice audit of 26 own videos (351 lines): videos built with a constant gap (0.2 or 0.38 s at every joint) had a gap spread of 0.01–0.08 s against 0.13–0.24 s in four approved reference videos; long pauses 2 of 160 joints against 11 of 57. The owner heard the regression before it was measured ("the voiceover got worse"). An earlier version of this recipe shipped the constant `GAP = 0.6`.

## Related
- [In-line pauses in F5](voice-f5-pauses.md)
- [Don't speed up the clone](voice-no-speedup-clone.md)
