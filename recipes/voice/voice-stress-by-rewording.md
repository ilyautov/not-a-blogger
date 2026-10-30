---
id: voice-stress-by-rewording
title: Fix wrong stress by replacing the word, not with marks; synthesize in chunks
section: voice
lang: ru
status: proven
evidence: ab-test
tools: [F5-TTS, WhisperX]
learn: ../../learn/en/03-voice.md
added: 2026-10-23
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
The Russian TTS model puts stress on the wrong syllable or hardens a consonant («модэль» for «модель», "model"; «флАгман», "flagship") or swallows an abbreviation. Stress marks `+`, doubled vowels, and hyphens work inconsistently. Per-sentence synthesis with even pauses flattens intonation.

## Do
1. Replace the mis-stressed word: «модель» → «какой телевизор» ("which TV"); rephrase «флагман».
2. Spell abbreviations as words or replace them: «ИИ» ("AI") → «нейросеть» ("neural network"), «GPT» → «джипити». Explain an unpronounceable term in Russian in speech; show it as-is on screen.
3. Try doubling the stressed vowel only as a last resort; check by ear.
4. Synthesize in chunks of 2–3 sentences, no stress marks, no speed-up. Trim by ASR: −0.12 s before the first word, +0.25 s after the last, with fades.

```python
REPLACE = {"ИИ": "нейросеть", "GPT": "джипити"}
def clean(line):
    for a, b in REPLACE.items():
        line = line.replace(a, b)
    return line.replace("+", "").replace("\u0301", "")   # drop stress marks, ASCII and Unicode
```

## Verify
ASR hears the whole word; the listener reports no wrong stress. Don't trust an energy probe for stress: once it reported success while the stress had not moved by ear.

## Don't
- Don't put Unicode stress marks (U+0301, «приве́т») into OmniVoice text: in one series they produced what the author called a heavy foreign accent (hypothesis, blind A/B pending; [gotchas](../../gotchas/lang/ru.md)). Strip them: `tools/voice/ru_tts_text.py`.
- Don't reuse a spelling across engines: OmniVoice read the same spelling differently; re-tune per engine.
- Don't trust an automatic accentuator blindly (it produced «+учит» instead of «уч+ит», "teaches"); dry-run it and inspect.
- Weight licenses: F5-TTS_RUSSIAN CC BY-NC 4.0, OmniVoice CC BY-NC. For commercial use pick an Apache-2.0 engine (e.g. VoxCPM2).

## Evidence
- «ИИ» from the clone was heard by ASR as «я» ("I"), 0.04 s long.
- «джи пи ти» was recognised as "G5", "ChatGPT" as «чад джи пяти».
- A/B on a talking head: chunks without marks — "great"; same text with manual `+` — "stress is just awful".
- Doubled vowel worked for one word (a stretched profanity, «Ахуееть», roughly "holy sh*t") and failed for «флагман». OmniVoice turned that spelling into «Охуеить».

Have the same issue in another language's TTS? Contribute a sibling recipe next to this one (lang: <code>).

## Related
- [Deterministic synthesis is fixed by text](voice-seed-fix-by-text.md)
- [Sacrificial first word](voice-f5-sacrificial-first-word.md)
- Example: [They said the same about DeepSeek](../../examples/deepseek-headlines/README.md)
- Example: [The mascot cancelled the call](../../examples/mascot-cancels-call/README.md)
