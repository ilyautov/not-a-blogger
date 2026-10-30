# Line-writing rules for a Russian TTS clone: brief block

lang: ru

Recording in another language? Contribute a sibling prompt next to this one.

- **Purpose:** a block pasted into the agent's brief before voice synthesis. It rewrites the lines so the clone does
  not swallow words or mangle stress.
- **Where tested:** F5-TTS (Russian model) with cloning, faster-whisper large-v3 for verification.
- **Status:** proven on dozens of videos; each rule closes a pitfall found via ASR on real takes.

## Prompt

The rules are in English; the Russian words the agent must use or avoid stay in Russian, with glosses.

```text
## Voice: rules for the lines (Russian TTS clone)
- The first line starts with the sacrificial word «Короче.» ("Anyway."). After synthesis it is cut out at the
  energy dip.
- Do not start a line with «Так» ("So"). The first word of a line starts with a consonant.
- Instead of «ИИ» ("AI") write «нейросеть» ("neural network"). Numbers as words. Write Latin-script names in
  Cyrillic as they are pronounced (for example «чат джи пи ти» for ChatGPT).
- Do not use "+" stress marks or Unicode accents (U+0301): "+" does not move the stress in F5, and U+0301 made
  OmniVoice sound like a heavy foreign accent. Replace a word with bad stress with a synonym.
- At most about one line in ten ends with "!": the clone doesn't act exclamations and may slip into falsetto.
- Synthesize in chunks of 2–3 sentences, no atempo speed-up. Pauses by meaning, not by punctuation.
- After synthesis, run ASR on every take (faster-whisper large-v3, ru, word_timestamps). A word swallowed or
  distorted means change the text, not the seed.
Video topic: {topic}. Rewrite the script lines in Russian by these rules and show a "before → after" table.
```

Short form, pasted as-is into the task of the agent that writes the lines (three bullets, nothing to negotiate):

```text
## Voice (F5 clone): rules learned from broken takes
- The first line starts with the sacrificial «Короче.»; no line starts with «Так»; the first word of a line starts
  with a consonant.
- «нейросеть» instead of «ИИ». Numbers in words. Latin names in Cyrillic as pronounced («Антропик», «Опен эй ай»,
  «чат джи пи ти»).
- After synthesis: ASR of every take (faster-whisper large-v3, ru, word_timestamps). A word swallowed or distorted
  means change the text, not the seed.
```

## Why

Russian TTS clones break predictably: on the first word, on Latin script, on numbers and on stress. Rewriting the
text before synthesis is cheaper than regenerating takes. With a fixed seed the result is deterministic, so sweeping
seeds does not cure a swallowed word; only different text does.

## Pitfalls

- A line starting with a vowel gets a stray "k" glued to the front; one starting with a consonant loses the first
  word entirely. Hence the sacrificial first word.
- The opening «Так,» collides with the model's internal lead token and gets clipped together with it.
- The model swallows «ИИ»; ASR writes «И» or a short «я». A line that opened «Попросил ИИ отменить…» ("asked the
  AI to cancel…") came out whole only after «ИИ» became «нейросеть». «Модель» ("model") is read with a hard "e": replace such words.
- "+" marks and doubled vowels did not move stress in F5 but did ruin intonation: «ударения прям ужас» ("the stress
  is just awful").
- Unicode stress marks (U+0301) on almost every word: the owner heard "a heavy accent" in an OmniVoice series. Videos
  that took off had 0 marks, the rest 47–433. Hypothesis until a blind A/B is heard; `tools/voice/ru_tts_text.py`
  strips them.
- «!» or «?!» in 67 % of lines against 10 % in approved references; OmniVoice didn't play them, one went falsetto.
- Dashes and ellipses give no pause; only the end of a sentence does (about 0.45 s).
- These rules are about the F5 wrapper; OmniVoice and other engines fail differently, retest before carrying them
  over ([omnivoice-clone-snippet.md](omnivoice-clone-snippet.md)).

Each rule has a measured recipe: [sacrificial first word](../../recipes/voice/voice-f5-sacrificial-first-word.md),
[pauses](../../recipes/voice/voice-f5-pauses.md), [tail word](../../recipes/voice/voice-f5-tail-sacrificial-word.md),
[fix by text, not seed](../../recipes/voice/voice-seed-fix-by-text.md),
[stress by rewording](../../recipes/voice/voice-stress-by-rewording.md),
[per-take ASR](../../recipes/qa/qa-asr-per-take.md). The vocabulary hint for that ASR:
[asr-vocabulary-hint.md](asr-vocabulary-hint.md). The full list of Russian TTS/ASR pitfalls:
[gotchas/lang/ru.md](../../gotchas/lang/ru.md).
