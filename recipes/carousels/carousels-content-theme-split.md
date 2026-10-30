---
id: carousels-content-theme-split
title: Keep card content in data and the look in a separate theme CSS file
section: carousels
lang: any
status: hypothesis
evidence: experience
tools: [python, weasyprint, pdftoppm]
learn: ../../learn/en/09-carousels-slides.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Card text and styles live in one script, so a new theme (dark, light, brand) means copying the whole script. A month later there are five copies and a bug fixed in one survives in four.

## Do
1. Card = data tuple; theme = one CSS file with the same class set in every theme.
2. Template builds HTML from tuple + theme CSS → weasyprint → PDF → pdftoppm → PNG.
3. New theme = copy the CSS and change variables.

```python
# cards.py: content only
CARDS = [
    ("01-cover", "BREAKDOWN", "1 / 6", "<h1>Title</h1><p>Subtitle</p>", False),
    ("02-fact",  "WHAT HAPPENED", "2 / 6", "<p>...</p>", False),
    # ...
    ("06-cta",   "WHAT TO DO", "6 / 6", "<p>...</p>", True),   # last: no "swipe"
]
```

```css
/* themes/paper.css: look only; same class set in all themes */
@page { size: 1080px 1350px; margin: 0 }
:root { --bg:#F4EFE6; --ink:#1C1917; --acc:#B5491F }
.label { ... } .card-num { ... } .bignum { ... } .foot { ... }
```

## Verify
The same `cards.py` renders in two themes with no code change.

## Don't
- Don't force a unique infographic (diagram, map) into the shared classes: keep it as a separate HTML fragment, same theme.

## Evidence
No own measurement.

## Related
- [Pre-render gate](carousels-prerender-gate.md)
- [Palette in :root](../brand/brand-palette-in-root.md)
