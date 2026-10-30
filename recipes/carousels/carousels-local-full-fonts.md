---
id: carousels-local-full-fonts
title: Load fonts as local full woff2 via @font-face, no Google Fonts, no subsets
section: carousels
lang: any
status: hypothesis
evidence: experience
tools: [weasyprint, fontTools]
learn: ../../learn/en/09-carousels-slides.md
added: 2026-10-23
updated: 2026-10-29
contributors: [not-a-blogger]
---

## When
`@import` of Google Fonts in weasyprint is slow or fails offline, and rendering falls back to a system font. "latin" or "cyrillic" subsets give tofu boxes on digits and Latin inside non-Latin text.

## Do
1. Download full font files once (all scripts you use, Latin, digits), keep them in the project, load via `file://`.
2. Put `@font-face` rules first in the CSS, no `.replace()` gluing.
3. Check the needed glyphs exist.
4. For serif and mono pick fonts covering your script (Georgia, DejaVu Serif, DejaVu Sans Mono). Georgia is a Microsoft system font: use it only as an installed font, never copy its files into a repo or package. Before committing any font file, read that font's own license and ship it next to the files: Inter and many Google Fonts are OFL, DejaVu has its own Bitstream Vera-derived license, other fonts may forbid redistribution.

```python
from pathlib import Path
FONTS = Path("fonts").resolve()
faces = "".join(
    f"@font-face{{font-family:'Inter';font-weight:{w};"
    f"src:url('file://{FONTS}/inter-{w}.woff2') format('woff2');}}"
    for w in (400, 500, 700, 800))
CSS = faces + THEME_CSS        # faces first
```

```bash
pip install fonttools brotli        # brotli is needed to read woff2
python3 -c "from fontTools.ttLib import TTFont as T; c=T('fonts/inter-400.woff2').getBestCmap(); print(all(ord(ch) in c for ch in 'Ёё0123456789?-%₽→'))"
```

Replace the test string with the characters your text uses.

## Verify
fontTools prints `True`. No boxes in digits or Latin on the rendered card.

## Don't
- Don't rely on variable fonts if weights look wrong: weasyprint support varies; use one static file per weight.

## Evidence
No own measurement. In a sandbox with a 45 s per-command limit, rendering with Google Fonts `@import` hit that limit.

## Related
- [Pre-render gate](carousels-prerender-gate.md)
