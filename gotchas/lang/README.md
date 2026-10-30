# Language-specific pitfalls

TTS and ASR break differently in every language: stress, numbers, abbreviations, the first and last word of a line.
One file per language, named by ISO 639-1 code. Same line format as [../README.md](../README.md): **what breaks**,
the number, the workaround. Write the file in English with native examples in quotes, so maintainers can review it.

| Language | File | Status |
|---|---|---|
| Russian | [ru.md](ru.md) | filled: F5-TTS, OmniVoice, Chatterbox, Whisper |
| English | [en.md](en.md) | waiting for contributions |
| German | [de.md](de.md) | waiting for contributions |
| Spanish | [es.md](es.md) | waiting for contributions |

Your language is missing? Copy [en.md](en.md), rename it and open a PR.
