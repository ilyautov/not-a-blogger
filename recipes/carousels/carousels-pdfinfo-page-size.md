---
id: carousels-pdfinfo-page-size
title: Check page size with pdfinfo after every weasyprint render
section: carousels
lang: any
status: proven
evidence: measurement
tools: [weasyprint, pdfinfo]
learn: ../../learn/en/09-carousels-slides.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
weasyprint silently drops an `@page` rule if junk precedes it in the CSS. The page falls back to A4, a 1080 px layout is cut on the right, no console error. Typical junk source: CSS gluing where `.replace()` hit the wrong string.

```python
# BAD: .replace binds only to the triple-quoted string; literal "X" stays first in CSS
CSS = "X" + """@page { size: 1080px 1350px; margin: 0 } ...""".replace("X", faces)
# GOOD
CSS = faces + """@page { size: 1080px 1350px; margin: 0 } ..."""
```

## Do
After every render check the page size. PDF uses points: 1 CSS px = 0.75 pt.

```bash
pdfinfo card.pdf | grep "Page size"
# 1080x1350 px  -> 810 x 1012.5 pts
# A4            -> 595 x 842 pts   (@page rule eaten)
```

## Verify
1080×1350 card: `810 x 1012.5 pts`. A4: `595 x 842` (or 595.276 x 841.89).

## Don't
- Don't reuse the px numbers for mm/in pages: recompute expected pt yourself (1 in = 72 pt).

## Evidence
A broken render produced A4 595×842 pt instead of the 1080 px layout; found only via pdfinfo, visually it looked like "right edge cut".

## Related
- [Rasterize px pages at -r 96](carousels-pdftoppm-96dpi.md)
- [Pre-render gate](carousels-prerender-gate.md)
