---
id: slides-check-pdf
title: Check a deck PDF by page count and a contact sheet, not by scrolling
section: slides
lang: any
status: hypothesis
evidence: experience
tools: [pdfinfo, pdftoppm, ffmpeg]
learn: ../../learn/en/09-carousels-slides.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The agent reports "PDF ready", yet a slide is missing, one was captured mid-transition, text overflows on another. No time to scroll 40 pages before the talk, and the eye glazes over.

## Do
1. Page count = slide count in HTML.
2. Contact sheet: all slides small on one image.
3. Look at the whole sheet: empty slides, twins, cut blocks. Open suspicious ones at full size (plate overflow is invisible in thumbnails).

```bash
pdfinfo deck.pdf | awk '/Pages/{print $2}'
grep -o 'class="slide' deck.html | wc -l

pdftoppm -r 18 -png deck.pdf th
ffmpeg -loglevel error -pattern_type glob -i 'th-*.png' -vf "tile=6x7:padding=6" -frames:v 1 sheet.png
```

## Verify
Both numbers match; no empty or repeated thumbnails on the sheet.

## Don't
- Don't keep `tile=6x7` for any deck: size the grid to the slide count (6x7 holds 42).
- Don't feed mixed page sizes to ffmpeg: it refuses to tile; normalize first.

## Evidence
No own measurement for decks. On video the same technique (dry review of 104 frames on contact sheets before render) found 6 layout defects and 2 invented numbers that no test caught.

## Related
- [Review the final contact sheet yourself](../qa/qa-contact-sheet-final.md)
- [HTML deck with PDF backup](slides-html-deck-with-pdf-backup.md)
