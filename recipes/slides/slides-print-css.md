---
id: slides-print-css
title: Add @media print to an HTML deck so printing gives one page per slide
section: slides
lang: any
status: hypothesis
evidence: experience
tools: [HTML/CSS, Chrome headless, pdfinfo]
learn: ../../learn/en/09-carousels-slides.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
In an interactive deck all slides are stacked (`position:absolute; display:none`) and one is shown. Print-to-PDF gives one page or a mess; a long scrolling slide gets cut.

## Do
1. Add a print block: each slide becomes a normal full-page block with a page break after it.
2. Print with headless Chrome (Linux: `chromium --headless ...`).

```css
@page { size: 1280px 720px; margin: 0 }
@media print {
  html, body { overflow: visible }
  .deck { height: auto }
  .slide { display: flex !important; position: relative; inset: auto;
           height: 100vh; opacity: 1 !important;
           break-after: page; page-break-after: always; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }  /* print backgrounds */
}
```

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
  --no-pdf-header-footer --print-to-pdf=deck.pdf "file://$PWD/deck.html"
pdfinfo deck.pdf | grep -E "Pages|Page size"
```

## Verify
PDF page count = number of `.slide` elements; text is selectable (`pdftotext deck.pdf - | head`).

## Don't
- Don't leave slides taller than the screen (`overflow-y:auto` in the show) as is: `height:100vh` cuts them; split in two or reduce font size in the print block.

## Evidence
A 42-slide deck for a 90-minute talk was printed this way. No measurement of broken-page share.

## Related
- [HTML deck with screenshot PDF backup](slides-html-deck-with-pdf-backup.md)
- [Check the deck PDF](slides-check-pdf.md)
