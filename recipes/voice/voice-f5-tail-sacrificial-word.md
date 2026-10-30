---
id: voice-f5-tail-sacrificial-word
title: Rescue the line ending with a sacrificial tail word and an alignment cut
section: voice
lang: any
status: proven
evidence: measurement
tools: [F5-TTS, WhisperX, ffmpeg]
learn: ../../learn/en/03-voice.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
F5-TTS clips the last sound of a line; mix ASR shows truncated words. The defect is in generation (the model did not finish), not at the segment boundary.

## Do
1. Before synthesis append a sacrificial word to every line, e.g. "… Uh-huh." (Russian «… Ага.»). Keep the clean text separately for captions.
2. Synthesize as usual: the real ending is no longer last, so the model finishes it.
3. Run WhisperX alignment (same as for karaoke) and cut at the start of the sacrificial word. Fade the tail over 50 ms.
4. If the recipe uses `atempo`, cut the unaccelerated file (aligner timings map onto it directly), then speed up.
5. Take durations change after the cut: recompute the timeline and karaoke.

```bash
# CUT = start of the sacrificial word from alignment, seconds
CUT=3.412
ffmpeg -y -i take.trim.wav -af "atrim=0:${CUT},afade=t=out:st=$(echo "$CUT-0.05"|bc):d=0.05" take.cut.wav
```

## Verify
ASR of the last 0.9 s of each take alone: if the sacrificial word is heard, the tail was not cut. Truncated words disappear from mix ASR.

## Don't
- Don't cut at the word boundary: the aligner puts it flush against the ending.
- Don't cut at the energy minimum: it falls on the closure before a plosive and a syllable is lost.
- Don't use `silenceremove` at −45 dB on the end: it eats the decay. Strip silence only from the start.
- F5-TTS_RUSSIAN weights are CC BY-NC 4.0.

## Evidence
- All six checked `.f5raw.wav` takes: zero seconds of tail silence, cut-off at −44 dB.
- The aligner sometimes swallows the final interjection; rescue those takes separately.

## Related
- [Rescue tails that were not cut](voice-tail-rescue-check.md)
- [Sacrificial first word](voice-f5-sacrificial-first-word.md)
