---
id: carousels-prerender-gate
title: Gate card text before rendering and the finished PDF with pdftotext after
section: carousels
lang: any
status: hypothesis
evidence: experience
tools: [python, pdftotext]
learn: ../../learn/en/09-carousels-slides.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Carousel errors show up only on published slides: "3 / 7" on card six, an em dash in a diagram label, boxes instead of a glyph, "17/30" on the cover read as a fraction though it's a date.

## Do
Two gates.

Before rendering, on card data (hard, render does not start):
- em dashes «—» = 0;
- "N / M" equals the card position and total;
- no "not just X but Y" / "not only X but also Y" constructions (use your language's patterns);
- last card flagged as last (no "swipe").

Warnings:
- glyphs missing from the font (`⏵ ⏴`) → replace with `→ ✓`;
- write dates as "15.06", not "15/06".

After rendering, on the finished PDF (catches dashes hidden in SVG labels and code).

```python
issues = []
for i, (name, label, num, body, last) in enumerate(CARDS, 1):
    if "—" in body + label: issues.append(f"{name}: em dash")
    if num.replace(" ", "") != f"{i}/{len(CARDS)}": issues.append(f"{name}: number {num}")
    if "not just" in body or "not only" in body: issues.append(f"{name}: contrast construction")
if not CARDS[-1][4]: issues.append("last card not flagged")
if issues: raise SystemExit("\n".join(issues))
```

```bash
pdftotext pack.pdf - | grep -c '—'     # must be 0
```

## Verify
Both gates empty; the last card has no swipe prompt.

## Don't
- Don't count on the gate for meaning or accuracy of product claims: that is a human read.

## Evidence
No own error-rate measurement. Dashes in SVG labels were found only by the second gate.

## Related
- [Humanize before TTS](../text/text-humanize-script-before-tts.md)
- [Check page size with pdfinfo](carousels-pdfinfo-page-size.md)
