---
id: carousels-pdftoppm-96dpi
title: Rasterize weasyprint px pages with pdftoppm -r 96, not 72
section: carousels
lang: any
status: proven
evidence: measurement
tools: [weasyprint, pdftoppm, sips]
learn: ../../learn/en/09-carousels-slides.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A card laid out at 1080×1350 px comes out as an 810×1013 PNG; the platform upscales it and text blurs. Cause: weasyprint writes 1 CSS px as 0.75 pt, and `pdftoppm -r 72` draws 1 pt as 1 pixel.

## Do
1. For px-sized pages rasterize at 96 dpi (96 / 72 = 1 / 0.75), or set pixel size explicitly.
2. To slice print A4 into slides, rasterize with headroom (`-r 200`), then downscale to the 1080×1350 canvas.

```bash
pdftoppm -r 96 -png -singlefile card.pdf card              # 1080x1350
pdftoppm -png -singlefile -scale-to-x 1080 -scale-to-y 1350 card.pdf card   # no arithmetic
sips -g pixelWidth -g pixelHeight card.png                 # check (macOS); or ImageMagick identify
```

## Verify
`sips` or `identify` shows exactly 1080×1350.

## Don't
- Don't use -r 96 for `@page` in mm or pt: pixels won't be round; use `-scale-to-x/-scale-to-y`.

## Evidence
The same card engine with `-r 72` produced a pack of 810×1013 PNGs; a sibling script with `-r 96` on the same layout gave 1080×1350. 0.75× per side.

## Related
- [Check page size with pdfinfo](carousels-pdfinfo-page-size.md)
- [Longread to PDF and carousel](carousels-longread-to-carousel.md)
