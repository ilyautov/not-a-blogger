---
id: voice-seed-fix-by-text
title: Fix a deterministic synthesis defect by editing text, not regenerating
section: voice
lang: any
status: proven
evidence: measurement
tools: [F5-TTS]
learn: ../../learn/en/03-voice.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A take has a clipped or garbled word and you are regenerating it repeatedly with a fixed seed.

## Do
1. Check determinism: generate the line twice and compare hashes.
2. If the files match, fix only via text: reorder words, change the opener, use a synonym, add a comma.
3. Change minimally; rerun ASR on the take.

```bash
python synth.py --seed 42 --text "$LINE" -o a.wav
python synth.py --seed 42 --text "$LINE" -o b.wav
shasum -a 256 a.wav b.wav     # identical → regeneration is useless
```

## Verify
Hashes of two runs match; after the text edit, take ASR matches the line.

## Don't
- Don't regenerate a deterministic engine hoping for a different result.
- For non-deterministic engines, judge the final take: regeneration does help there.
- Weight licenses: F5-TTS_RUSSIAN CC BY-NC 4.0, OmniVoice CC BY-NC. For commercial use pick an Apache-2.0 engine (e.g. VoxCPM2).

## Evidence
- F5-TTS with seed 42: resynthesis produced a byte-identical file.
- In one long video four lines with broken words were fixed by text changes only.
- A word compressed by the model (Russian «Заголовок», "headline", came out as «Заголок») was restored by a comma after it.
- In the blind test one Apache-licensed engine produced different words run to run.

## Related
- [Stress by rewording](voice-stress-by-rewording.md)
- [Per-take ASR](../qa/qa-asr-per-take.md)
