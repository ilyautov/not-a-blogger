---
id: sound-no-soft-clip-master
title: Master the voice mix linearly with loudnorm and a −2 dBFS limiter, never through tanh or a soft clip
section: sound
lang: any
status: proven
evidence: measurement
tools: [ffmpeg, ebur128]
learn: ../../learn/en/06-sound-captions.md
added: 2026-10-28
updated: 2026-10-29
contributors: [not-a-blogger]
---

## When
A mix script (yours or an engine's) has a line like `mix = tanh(mix * 1.15) / 1.15` "to avoid clipping", or a limiter with a low ceiling. The video hits −14 LUFS, but the voice sounds flat and pressed, and true peak sits far below the ceiling.

## Do
1. Remove any `tanh`, soft clip or saturation from the master bus. Sum the tracks linearly.
2. Level with `loudnorm` to the target in [QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md) (−15 LUFS ±1, TP −1.5 on the encoded file).
3. If a limiter is needed, set its ceiling at −2 dBFS, not lower.
4. Keep `level=false` on `alimiter`: its default auto-level raises the whole mix after limiting and pushes loudness and true peak past the targets (a synthetic test: −13.2 LUFS / −0.9 dBTP with the default, −15.2 / −2.9 with `level=false`).
5. Re-mix from the existing takes: no re-synthesis needed.
6. Measure the final encoded file (AAC/MP4), not `master.wav`: encoding moves true peak.

```bash
ffmpeg -i voice.wav -i music.wav -filter_complex \
  "[1]volume=0.3[m];[0][m]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-3:LRA=7,alimiter=limit=0.794:level=false[a]" \
  -map "[a]" -ar 48000 master.wav          # 0.794 = −2 dBFS; level=false: no auto make-up gain
```

## Verify
`ebur128=peak=true` on the encoded file: true peak between −2.5 and −1.5 dBTP at the target loudness. `tools/qa/voice_qa.py` passes `true_peak`.

## Don't
- Don't "fix" a peak warning with a soft clip: it moves the problem into every syllable.
- Don't expect a linear re-mix to raise LRA: in the measured case it didn't (2.0 → 1.9). Flat dynamics also come from the takes and the script.

## Evidence
- 12 videos mixed through `tanh`: in 35–39 % of speech frames peaks were pressed by more than 1 dB, at most by 4–7 dB; true peak −4.4 dBTP at −14 LUFS, LRA 1.5–2.2.
- One of them re-mixed linearly with a −2 dBFS limiter ceiling (was −4.5): true peak −4.2 → −1.9 dBTP, speech crest factor +1 dB.
- Whether the squashed mix cost views could not be separated from upload slots: those videos went out on the day after a mass upload, when all uploads got low views.

## Related
- [Loudness like hits](sound-loudness-like-hits.md)
- [Voice gate](../qa/qa-voice-gate.md)
