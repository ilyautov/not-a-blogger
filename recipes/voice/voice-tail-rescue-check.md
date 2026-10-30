---
id: voice-tail-rescue-check
title: Check every take's tail and rescue uncut ones by energy
section: voice
lang: any
status: proven
evidence: measurement
tools: [faster-whisper, WhisperX, numpy, ffmpeg]
learn: ../../learn/en/03-voice.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
After cutting at the sacrificial tail word, some takes still contain it (the aligner swallowed the final interjection and the script logged "word not found, take left as is"). Or an engine clips the ending and the mix hides it.

## Do
1. After the cut, list takes without a cut version. "Word not found" does not mean clean.
2. For each, cut the last 0.9 s and run ASR alone. If the sacrificial word is heard, the tail is still there.
3. Cut those takes by energy, without ASR: find the last loudness dip and drop everything after it. Guard: removed tail length 0.25–1.4 s.
4. If the tail is fused with speech and there is no dip, shorten the line and resynthesize.
5. For any engine, detect clipping by signal: if the last 30 ms of speech are louder than peak −30 dB, the sound breaks off instead of decaying.

```python
import numpy as np, soundfile as sf
def is_clipped_end(path, tail_ms=30, rel_db=-30):
    x, sr = sf.read(path); x = x if x.ndim == 1 else x.mean(1)
    nz = np.nonzero(np.abs(x) > 1e-4)[0]; x = x[: nz[-1] + 1]
    peak = 20*np.log10(np.abs(x).max() + 1e-12)
    tail = x[-int(sr*tail_ms/1000):]
    return 20*np.log10(np.sqrt((tail**2).mean()) + 1e-12) > peak + rel_db
```

```bash
# last 0.9 s alone for ASR
ffmpeg -y -sseof -0.9 -i voice-17.wav tail.wav
```

## Verify
ASR of the last 0.9 s of every take has no sacrificial word; the clipping detector is silent.

## Don't
Don't reuse the −30 dB threshold on quiet or noisy recordings: it was tuned on lines normalised to −16 LUFS, the per-take level from [QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md).

## Evidence
- Long video, 246 takes: in 34 (14 %) the sacrificial word survived the alignment cut.
- Blind TTS test, four lines: the "last 30 ms louder than peak −30 dB" rule found clipping in four of five engines tested without a tail word (F5 always ran with one). One engine clipped 1 line of 4, the others 3–4.

## Related
- [Sacrificial tail word](voice-f5-tail-sacrificial-word.md)
- [Per-take ASR](../qa/qa-asr-per-take.md)
- [Blind TTS bake-off](voice-blind-tts-bakeoff.md)
