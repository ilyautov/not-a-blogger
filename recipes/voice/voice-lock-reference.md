---
id: voice-lock-reference
title: Don't change the clone's reference audio without a blind A/B by the voice owner; watch median pitch
section: voice
lang: any
status: proven
evidence: measurement
tools: [librosa, ffmpeg]
learn: ../../learn/en/03-voice.md
added: 2026-10-28
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
Someone (often an agent in another session) swaps the reference clip of a voice clone for a "cleaner" or "fresher" recording, or changes the speed or engine setting. Nobody asks the owner; a few videos later the voice "is not mine anymore".

## Do
1. Keep one approved reference per voice in a canon file: path, sha256, engine, speed, date of approval, who approved.
2. Synthesis scripts read the reference from the canon file only; no hard-coded paths in per-video scripts.
3. A new candidate reference goes through a blind A/B: same 3–5 lines, both references, labels hidden (A/B key in a separate file). The person picks; only then the canon file changes.
4. In QA compare the median pitch of the new video's voice with the approved reference. A shift of more than 1 semitone means a different reference or setting.

```python
import math
def semitones(f_new, f_ref):            # median F0 in Hz
    return 12 * math.log2(f_new / f_ref)
assert abs(semitones(f0_video, f0_canon)) <= 1, "voice drifted from the approved reference"
```

## Verify
The sha256 of the reference used in the build equals the canon file's; the pitch shift is within ±1 semitone; the canon file's history shows an A/B for every change.

## Don't
- Don't change the reference, speed or engine "silently because it's better": the person hears it before any metric does.
- Don't run the A/B with labels visible or with different texts.

## Evidence
- One clone quietly switched to another reference recording: pitch went up 2–3 semitones (median F0 85 → 96–101 Hz) and treble dropped 3–5 dB. It coincided with the owner hearing a regression; the voice audit then confirmed it.
- The same series also had a speed setting of 1.1 against the agreed 1.0.
- Views could not separate the reference from upload-slot effects: in one same-day comparison the swapped voice scored the same as the approved one (1,067 against 972 and 1,146 views).

## Related
- [Blind TTS bake-off](voice-blind-tts-bakeoff.md)
- [Don't speed up the clone](voice-no-speedup-clone.md)
- [Voice gate](../qa/qa-voice-gate.md)
