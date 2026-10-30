---
id: text-scanner-misses-form-slop
title: Don't read a scanner's "clean" as proof of a living script
section: text
lang: any
status: proven
evidence: measurement
tools: [humanizer-ru]
learn: ../../learn/en/02-text-humanizer.md
added: 2026-10-23
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
Text scanners catch words and constructions (clichés, officialese, dashes, triplets), not form slop: a "top 3" template on a topic that isn't a list, a characterless announcer persona, the third video in a row on one skeleton. They pass as "clean"; viewers spot the assembly line in seconds.

## Do
The scanner covers the vocabulary layer. Check form separately before building, with five questions:
1. Is the topic really a list? If not, "first/second/third" is forced.
2. Summarize the video in one sentence without "first", "second", "third". Possible? Then there is a plot.
3. Does the character have personality (reaction, opinion, joke) or read out bullet points?
4. Was this skeleton (background, card, plate, block order) in the two previous videos?
5. Does the "after" example prove something, or is it bland? A high score on corporate text proves nothing.

Any wrong answer: rewrite the script, not the words.

```bash
uvx ru-humanizer script.txt          # vocabulary layer
# form: answer the five questions in meaning.md next to the script
```

## Verify
A person who hasn't seen the script retells the video after one viewing in their own words, with no numbering.

## Don't
- Don't apply question 1 to real lists (hotkeys, commands, install steps): they legitimately live as "top N".

## Evidence
- A humanizer reel on a "top 3" template was rated "neuroslop" by the editor; the scanner caught only the quotes in its script.
- A reel of five ChatGPT-written greetings with "beyond it" in 4 of 5: scanner 91–98, band "clean". Editor's rating: "slop".
Scanner scores (91–98, band "clean") against the approver's verdict on 2 reels; the 4-of-5 count is from the greetings reel.

## Related
- [Script before build, don't repeat the skeleton](../idea/idea-script-before-build.md)
- [Humanize before TTS](text-humanize-script-before-tts.md)
