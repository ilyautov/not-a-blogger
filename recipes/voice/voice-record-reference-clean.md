---
id: voice-record-reference-clean
title: Record the voice on a phone and remove mouth clicks before cloning
section: voice
lang: any
status: proven
evidence: measurement
tools: [ffmpeg, F5-TTS, OmniVoice]
learn: ../../learn/en/03-voice.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Preparing a clone reference or a live voice-over. The clone copies everything in the reference, including clicks.

## Do
1. Record reference and live takes on a phone (stock voice recorder), not a laptop mic and not wireless earbuds (they record at 16 kHz).
2. If only a laptop recording exists, run `adeclick` twice before cloning.
3. Count clicks before and after with the same `adeclick`.

```bash
ffmpeg -y -i ref.wav -af "adeclick=w=55:o=75:t=2,adeclick=w=55:o=75:t=2" ref-dc.wav
# rough SNR: speech level vs pause level
ffmpeg -i ref.wav -af "astats=metadata=1:reset=0" -f null - 2>&1 | grep -E "RMS level|Noise floor"
```

## Verify
Synthesis on the cleaned reference does not crackle; click count on the reference is near zero.

## Don't
- Don't read the `adeclick` count as absolute: it also fires on sharp synthetic consonants. Use it only to compare variants.
- Don't run speech "enhancers" blindly: they can damage the first word.
- Weight licenses: F5-TTS_RUSSIAN CC BY-NC 4.0, OmniVoice CC BY-NC. For commercial use pick an Apache-2.0 engine (e.g. VoxCPM2).

## Evidence
- Laptop recording: 385 clicks in 34 s vs 1 for an older clean recording. `adeclick` ×2 cut the count from 83 to 8.
- Same counter: raw reference 336 clicks per minute, cleaned 0.
- Phone vs laptop: SNR 41 dB vs 33.
- In one A/B an enhancer turned «Короче» ("anyway") into «Корч».

## Related
- [Blind TTS bake-off](voice-blind-tts-bakeoff.md)
- [Live voice for the character](voice-live-for-character.md)
- Prompt: [OmniVoice clone snippet](../../prompts/voice/omnivoice-clone-snippet.md)
- Example: [I handed my Instagram to the agent](../../examples/instagram-to-claude-skit/README.md)
