---
id: text-modern-chatgpt-tells
title: Grep fresh model text for em dashes, triplets and "a new stage", not old clichés
section: text
lang: ru
status: proven
evidence: measurement
tools: [ru-humanizer, grep]
learn: ../../learn/en/02-text-humanizer.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Lists of AI-text tells go stale. A fresh model barely writes «стоит отметить» ("it is worth noting") or «в современном мире» ("in today's world"), so Russian text looks clean, yet viewers still recognize it.

## Do
Search for what models leave now:
- em dash «—»;
- comma triplets («быстро, удобно и надёжно»);
- «новый этап» ("a new stage"), «впереди» ("ahead"), «за её/его пределами» ("beyond it");
- stock politeness like «рад присоединиться» ("glad to join").

```bash
grep -n -E '—|новый этап|впереди|за (её|его|их) пределами|рад присоединиться' script.txt
grep -n -E '[[:alpha:]]+, [[:alpha:]]+ и [[:alpha:]]+' script.txt     # triplet candidates
uvx ru-humanizer script.txt
```

## Verify
Both grep commands return nothing, or every match is kept deliberately.

## Don't
- Don't strip dashes in direct speech or in genres where they are the norm (reference, legal).
- Don't break a genuine list of three things.

## Evidence
ChatGPT texts from a clean profile without custom instructions scored 78–91 on the scanner with zero «стоит отметить». They were given away by dashes, «новый этап», comma triplets, «впереди», «рад присоединиться». Under a video on this topic viewers joked by commenting a single dash.

## Related
- [Humanize before TTS](text-humanize-script-before-tts.md)
- [Don't treat "clean" as a living script](text-scanner-misses-form-slop.md)
- Example: [AI text gives itself away, but not by the old clichés](../../examples/ai-text-tells/README.md)

Writing in another language? Contribute a sibling recipe next to this one (lang: <code>).
