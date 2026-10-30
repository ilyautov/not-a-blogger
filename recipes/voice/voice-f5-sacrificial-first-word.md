---
id: voice-f5-sacrificial-first-word
title: Make the first word of a line sacrificial and consonant-initial
section: voice
lang: ru
status: proven
evidence: measurement
tools: [F5-TTS, WhisperX]
learn: ../../learn/en/03-voice.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The F5-TTS cloning wrapper prepends a lead token (Russian «Так,», "So,") and cuts it by ASR timestamps. The cut is imprecise: a vowel-initial line keeps a stray "k" («Отличие от файла», "The difference from the file", becomes «К отличии…»); a consonant-initial line loses its whole first word («Дальше про два дома», "Next, about two houses", becomes «Про два дома»); a line starting with the token word itself («Так что…», "So…") loses a real word.

## Do
1. Start the line with a word whose loss breaks nothing: «Главное отличие от файла проекта…» ("The main difference from the project file…").
2. Start with a consonant and a word longer than four letters.
3. Never start with the lead-token word («Так», «Так,»). Reorder short openers the model swallows: «Шаг шестой» → «Шестой шаг» ("Step six" → "Sixth step").
4. Run ASR on every take separately, before assembly.

```python
import re
LEAD = "так"
def first_word_warnings(line: str) -> list[str]:
    w = re.findall(r"[\wёЁ-]+", line.lower())
    if not w:
        return []
    out = []
    if w[0] == LEAD:
        out.append("starts with the lead-token word")
    if w[0][0] in "аеёиоуыэюя":
        out.append("vowel-initial: a stray 'k' will remain")
    if len(w[0]) < 4:
        out.append("first word shorter than 4 letters: may vanish")
    return out
```

## Verify
Per-take ASR of each `voice-N.wav`: the first word is present, or only the sacrificial one is gone. Don't check on the final mix ASR: it hides these takes.

## Don't
- Don't apply blindly to OmniVoice or other engines: the rule is about this F5 wrapper's lead-token mechanism; retest.
- F5-TTS_RUSSIAN weights are CC BY-NC 4.0: non-commercial use only.

## Evidence
- Long video, 97 takes: three lost their first word to the lead token; found only by per-take ASR.
- «Так что Китай сделал…» ("So China did…") was recognised after synthesis as «за китай сделал…».

Have the same issue in another language's TTS? Contribute a sibling recipe next to this one (lang: <code>).

## Related
- [F5 pauses: full stop and marker only](voice-f5-pauses.md)
- [Sacrificial tail word](voice-f5-tail-sacrificial-word.md)
- [Per-take ASR](../qa/qa-asr-per-take.md)
- Prompt: [F5 line rules block for the script agent](../../prompts/voice/tts-script-rules.md)
