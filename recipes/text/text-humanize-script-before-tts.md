---
id: text-humanize-script-before-tts
title: Run the script through the humanizer before voice synthesis
section: text
lang: ru
status: proven
evidence: measurement
tools: [humanizer-ru, ru-humanizer]
learn: ../../learn/en/02-text-humanizer.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A model-written Russian script sounds like an announcer: "not X but Y" every other sentence, comma triplets, "a new stage", em dashes. Caught after synthesis, it costs re-voicing takes and re-timing.

## Do
1. Put all lines in one file, one line per line of dialogue, no timecodes or stage notes.
2. Scan with [humanizer-ru](https://github.com/ilyautov/humanizer-ru) (MIT, package `ru-humanizer`).
3. Give the text to an agent with the humanizer-ru skill: "edit as a voice-over script: conversational, short sentences, don't touch the hook and the final CTA".
4. Compare before/after with the same scanner: score before/after + fact lock on numbers and names.
5. Only then start synthesis.

```bash
uvx ru-humanizer script.txt --json > scan-before.json      # or: pipx install ru-humanizer
# agent edit with the skill -> script.v2.txt
uvx ru-humanizer script.v2.txt --before script.txt         # score before/after + fact lock
```

Keep the "choppy meditative" penalty (3+ consecutive lines of 1–3 words, like "Delete. Please. Now.") in dialogue: people talk that way.

## Verify
Band "clean", empty hard-ban list, fact lock shows no lost numbers. No "not just" audible in the voice-over.

## Don't
- Don't treat the scanner as a plot check: it sees words and constructions, not formulaic form, see [form slop](text-scanner-misses-form-slop.md).
- Don't mix scanner versions in one before/after: the browser version doesn't compute nominality (noun/verb ratio) and scores up to 8 higher than the Python version.
- Don't expect it to catch words the TTS mispronounces: that is a separate ASR check.

## Evidence
- 10 dialogue reel scripts (45–50 s each): all in the "clean" band, scores 92–100. Minus 8 points in two of ten came from choppy meditative dialogue lines; left unedited.
- On fresh ChatGPT texts the skill edit matters only in some genres: 77 → 100 in one, 80 → 80 in others. A clean input has little to fix.

## Related
- [Don't treat "clean" as a living script](text-scanner-misses-form-slop.md)
- [Before/after fact lock](text-fact-lock-before-after.md)
- [Tells of fresh model text](text-modern-chatgpt-tells.md)

Writing in another language? Contribute a sibling recipe next to this one (lang: <code>).
