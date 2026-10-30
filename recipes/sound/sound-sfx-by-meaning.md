---
id: sound-sfx-by-meaning
title: Assign SFX by event meaning and tune tonal SFX to the track's tonic
section: sound
lang: any
status: hypothesis
evidence: viewer-feedback
tools: [Python, numpy, ffmpeg]
learn: ../../learn/en/06-sound-captions.md
added: 2026-10-23
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
The SFX synth has fourteen kinds but videos use the same three; tonal effects clash with the music key.

## Do
1. Put SFX on on-screen events, not on every tween: grab, impact, shot change, number appears.
2. Map kinds by meaning: click, impact, whoosh, hiss, sweep, tick, tone, buzz, step, riser, glitch, thud, chime, whip.
3. Build tonal ones (chime, tone, tick, step) from the track's tonic on the major pentatonic: each video gets its own tuning.
4. Camera-move sounds: smash cut = impact + whoosh exactly on the frame; whip pan = noise with rising band; freeze frame = silence + chime ≈1760 Hz; jump cut = click on each change.
5. Time steps and hits from story time, so they thin out in slow-mo and vanish in a freeze.

```python
import numpy as np
PENTA = [0, 2, 4, 7, 9]                       # major pentatonic, semitones
def note(tonic_hz, step):                      # step = 0,1,2…
    octave, deg = divmod(step, 5)
    return tonic_hz * 2 ** ((PENTA[deg] + 12 * octave) / 12)
def chime(f, dur=0.6, sr=44100):
    t = np.arange(int(sr * dur)) / sr
    return (np.sin(2*np.pi*f*t) + 0.3*np.sin(2*np.pi*2*f*t)) * np.exp(-6*t)
```

## Verify
The SFX timeline has at least 5–6 kinds, each tied to an event; tonal notes match degrees of the track's tonic.

## Don't
- Don't use sound to mask an empty plot: it works only where action changes.
- Don't put a buzz or impact SFX on top of the hook word: under it ASR lost the word (one video), and the viewer may lose it too. Place the hit before or after the word.

## Evidence
No effect measurement. Trigger: "same sound effects" with three of fourteen kinds used; after mapping eleven kinds by meaning the video was accepted and published.

## Related
- [Keep noise whooshes](sound-keep-noise-whooshes.md)
- [J- and L-cuts](../transitions/transitions-j-l-cut.md)
- Example: [Assistant cancels a call](../../examples/mascot-cancels-call/README.md)
