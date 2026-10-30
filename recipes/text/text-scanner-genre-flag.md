---
id: text-scanner-genre-flag
title: Pass the text genre to the scanner so legitimate register isn't penalized
section: text
lang: ru
status: proven
evidence: measurement
tools: [ru-humanizer]
learn: ../../learn/en/02-text-humanizer.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The Russian scanner defaults to marketing. Reference, legal or news text legitimately uses em dashes and officialese and gets penalized for its own genre norms.

## Do
Pass the genre with `--genre`: `marketing` (default), `academic`, `legal`, `fiction`, `news`. Keep video scripts and posts on `marketing`.

```bash
uvx ru-humanizer article.md --genre academic
uvx ru-humanizer contract.txt --genre legal
uvx ru-humanizer script.txt                  # script: default genre
```

## Verify
A known human text of its genre lands in the "clean" band.

## Don't
- Don't compare exact scores across genres: the genre flag doesn't lift the nominality penalty (many nouns per verb), so even human academic text won't reach 100. Compare bands.

## Evidence
Three verbatim Wikipedia excerpts with `academic`: scores 89, 92, 92, all "clean" (false-positive control from the humanizer-ru eval).

## Related
- [Humanize before TTS](text-humanize-script-before-tts.md)

Writing in another language? Contribute a sibling recipe next to this one (lang: <code>).
