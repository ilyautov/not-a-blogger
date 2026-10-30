---
id: voice-blind-tts-bakeoff
title: Choose the TTS engine by a blind test with a numbered key
section: voice
lang: any
status: proven
evidence: ab-test
tools: [F5-TTS, OmniVoice, VoxCPM2, Qwen3-TTS, CosyVoice3, Chatterbox, faster-whisper]
learn: ../../learn/en/03-voice.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Picking or replacing a TTS engine. Don't decide from vendor demos or names; ASR barely separates engines and does not hear stress at all.

## Do
1. One reference; the same 3–4 lines from a real video plus one hard line (profanity, tricky stress).
2. Identical conditions: fixed seed, no speed-up, all lines normalised to one loudness, edge silence removed.
3. Name variants `01…06`; keep the "number → engine" key in a separate file, open it only after listening.
4. The listener gives verdicts by number. Keep generation time and memory out of the blind part: they reveal the engine.
5. Separately compute: syllables per second, clicks, longest pause, clipped endings, lost and garbled words by ASR.

```bash
for i in 01 02 03 04 05 06; do
  ffmpeg -y -i raw/$i.wav -af "silenceremove=start_periods=1:start_threshold=-50dB,loudnorm=I=-16:TP=-2" -ar 44100 -ac 1 blind/$i.wav
done
# beep before each variant when concatenating
ffmpeg -f lavfi -t 0.3 -i "sine=f=1000:sample_rate=44100" beep.wav
```

## Verify
Listener verdict recorded by number before the key is opened; the winner has no lost words by ASR.

## Don't
- Don't transfer rules found for one engine (sacrificial word, tail) to another without retesting.
- Don't disable Chatterbox's (MIT) Perth watermark.
- Licenses: OmniVoice code Apache-2.0, weights CC BY-NC (Emilia data), audio tokenizer under a separate community license. F5-TTS_RUSSIAN: CC BY-NC 4.0. Fish S2-Pro: research license. For commercial use: VoxCPM2, Qwen3-TTS, CosyVoice3 (Apache-2.0).

## Evidence
Blind test of six engines on one reference (compute seconds per 1 s of speech, Apple M1 Max):
- chosen OmniVoice: 1.35 s, closest to live tempo (5.77 syll/s vs 5.48 for the reference), clipped ending in 1 line of 4;
- VoxCPM2: 1.23 s, "fine", but clicks the most;
- F5-TTS: 4.84 s, fastest speech (6.12 syll/s), near-zero pauses between sentences, clips the ending without a tail word;
- Fish S2-Pro: 3.45 s, peak memory 28.7 GB, worst rating.
- All six had no lost words by ASR: the ear decided.
- Chatterbox on Russian separately: 4.5 syll/s vs 5.4 for F5, floating stress; fine for English (exaggeration 1.1, cfg_weight 0.4, seed 42).

## Related
- [Clean reference](voice-record-reference-clean.md)
- [Tail check](voice-tail-rescue-check.md)
- [Don't speed up the clone](voice-no-speedup-clone.md)
- Prompt: [OmniVoice clone snippet](../../prompts/voice/omnivoice-clone-snippet.md)
