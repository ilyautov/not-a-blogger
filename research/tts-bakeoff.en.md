[Русская версия](tts-bakeoff.md)

# A blind test of six TTS engines on a Russian voice clone

October 2026, Apple M1 Max, 64 GB. Goal: find an engine to clone our own voice for reels. The owner of the voice listened
himself and rated blind; the numbers were assigned at random.

## Conditions

- One reference for all: 7.3 s of a live recording, cleaned of clicks (`adeclick`).
- Four lines from a real video, including an emotional interjection with a stretched vowel.
- Native tempo, no `atempo`. Seed 42. Engines were run strictly one at a time.
- Tail clipping was checked automatically: if the last 30 ms are louder than peak −30 dB, the sound is cut off rather
  than fading out. In that case the line was regenerated with a sacrificial tail, which was then trimmed using ASR.
- All files normalized to −16 LUFS, TP −2.

## Listening results

| Engine | Listener's verdict | Generation, s per 1 s of speech | Peak memory, GB | Tail clipping | Weights license |
|---|---|---|---|---|---|
| OmniVoice | **best**, «больше всего понравилось» [liked it the most] | 1.35 | 4.4 | 1 of 4 | CC BY-NC |
| VoxCPM2 | «норм» [fine] | **1.23** | 13.3 | 3 of 4 | Apache-2.0 |
| Qwen3-TTS 1.7B | «хочется быстрее» [wish it were faster] | 1.66 | 6.1 | 4 of 4 | Apache-2.0 |
| CosyVoice3 0.5B | no opinion | 4.50 (on CPU) | 7.6 | 0 of 4 | Apache-2.0 |
| F5-TTS, Russian model | not chosen | 4.84 | 4.5 | always, tail fixed per recipe | CC BY-NC |
| Fish Audio S2-Pro | worst | 3.45 | 28.7 | 4 of 4 | research only |

Didn't make the cut: OpenAudio S1-mini (closed weights), Fish Audio Drama 3 (NVIDIA only), IndexTTS2 (no Russian).

## What the numbers showed

- **ASR can't tell the engines apart.** None of them dropped words. ASR doesn't see stress at all, and stress is the main
  complaint. Only the ear decides.
- **"Cleanest" by the metrics doesn't mean best.** CosyVoice3 clicked the least and never clipped a tail, but turned out
  slower than the live voice (4.85 syllables/s vs 5.48) and flat in intonation.
- **A fast tempo with no pauses sounds like gabbling.** F5 ran 12% faster than the reference, with almost no pauses
  between sentences.
- **Interjections with a stretched vowel break differently in different engines.** Two of the six inserted an extra
  sound. Tune the spelling to the specific engine.

## Conclusions

1. For non-commercial videos, OmniVoice fits: 3.6× faster than F5 and clips the tail less often.
2. If the videos will be monetized, pick a model under Apache-2.0. Of those tested, VoxCPM2 comes closest to the best.
3. Recipes for one engine (a sacrificial first word, the tail) don't carry over to another blindly; they have to be
   re-tested.

## How to repeat it

You need a "number → engine" key in a separate file the listener can't see, the same text and reference for everyone,
loudness normalization, and one concatenation of all variants in a row with a beep between them. More detail in the
blind A/B recipe in `recipes/voice/`.
