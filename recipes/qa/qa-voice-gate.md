---
id: qa-voice-gate
title: Gate the voice before showing the video: peaks, loudness range, gap spread, rate, pitch
section: qa
lang: any
status: proven
evidence: measurement
tools: [ffmpeg, ebur128, librosa]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-28
updated: 2026-10-29
contributors: [not-a-blogger]
---

## When
Before showing a finished video to the person. Every other check is green, ASR matches the script, but over a series the voice "got worse" and nobody can say why. Usual causes: a soft-clip master, a metronome of gaps, shortest-take picking, a quietly swapped clone reference.

## Do
1. Export the line timings of the final file: `[{"id", "text", "start", "end"}]`, seconds from the start of the file. Add `"file"` per line or pass `--voice` (voice track without music) to get pitch.
2. Pick the voice profile. The 250 Hz pitch ceiling was calibrated on one male clone only. For that profile keep it. For any other voice, measure the median F0 of your approved reference and set `--f0-max` a little above it; until you have such a reference, treat pitch as a diagnostic (read the values, don't drop takes on them).
3. Run the gate on the encoded final:

```bash
# calibrated male-clone profile
python3 tools/qa/voice_qa.py output/final.mp4 --lines voice/timing.json --voice voice/voice.wav \
    --json qa/voice-qa.json
# other voice: ceiling from your approved reference (example value); until calibrated add --f0-diagnostic
python3 tools/qa/voice_qa.py output/final.mp4 --lines voice/timing.json --voice voice/voice.wav \
    --f0-max 320 --json qa/voice-qa.json
```

4. Thresholds (values and origin: [QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md)): true peak ≥ −2.5 dBTP, LRA ≥ 2.5 LU, standard deviation of gaps ≥ 0.1 s, each line ≤ 6.3 syllables/s; median pitch per line ≤ 250 Hz for the calibrated male-clone profile only.
5. A fail points at its fix: low true peak → [no soft clip](../sound/sound-no-soft-clip-master.md); low gap spread → [gaps from the script](../voice/voice-gaps-between-lines.md); fast lines → re-pick the take by median duration ([per-take ASR](qa-asr-per-take.md)); high pitch on a calibrated profile → drop the take, check the [clone reference](../voice/voice-lock-reference.md).
6. Put the report next to `final-result.json` and tell the person which checks ran and which didn't (no voice track = pitch not measured).

## Verify
`qa/voice-qa.json` exists, `pass` is true (with `--f0-diagnostic` on an uncalibrated voice, `f0_over` is reported but left out of `pass`, and the report has `"f0_diagnostic": true`), and the summary lists every check with its value; a `—` check (not measured) is named in the report to the person.

## Don't
- Don't treat a pass as "the voice is good": the thresholds came from one author's approved references and were never calibrated on views. A pass rules out four known regressions, nothing more; the person listens.
- Don't tighten or loosen a number in a recipe: change it in docs/QA-THRESHOLDS.md first.
- Don't measure pitch on the mixed track: music drags the estimate. Without a clean voice, leave pitch unmeasured.

## Evidence
Audit of 26 own videos (351 lines) after the author said "the voiceover got worse", against four approved reference videos on the same clone:
- 12 videos mixed through `tanh`: 35–39 % of speech frames squashed by more than 1 dB (up to 4–7 dB), true peak −4.4 dBTP at −14 LUFS, LRA 1.5–2.2.
- Constant gaps: spread 0.01–0.08 s against 0.13–0.24 s; long pauses 2 of 160 joints against 11 of 57.
- Shortest-take picking: two videos 15 % faster than the references.
- A swapped clone reference: +2–3 semitones (85 → 96–101 Hz) and 3–5 dB less treble.
- Not confirmed: clipped tails, swallowed words and level jumps between takes were not the cause.
The gate detects these regressions; whether its thresholds predict views is not measured.

## Related
- [Linear master, no soft clip](../sound/sound-no-soft-clip-master.md)
- [Gaps from the script](../voice/voice-gaps-between-lines.md)
- [Lock the clone reference](../voice/voice-lock-reference.md)
- [Green is not approval](qa-green-is-not-approval.md)
