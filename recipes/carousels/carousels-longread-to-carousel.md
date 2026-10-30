---
id: carousels-longread-to-carousel
title: Build an A4 PDF and a 1080×1350 carousel from one article by slicing pages
section: carousels
lang: any
status: hypothesis
evidence: video-metric
tools: [weasyprint, pdftoppm, Pillow, pdftotext]
learn: ../../learn/en/09-carousels-slides.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A longread is needed as a PDF document (LinkedIn, download) and a swipe carousel (Telegram, Threads, Instagram). Laying out two versions by hand doubles work and numbers drift apart.

## Do
One source, one layout, carousel by slicing.
1. A4 PDF: one topic = one page (`break-before: page` on H2), data in callouts (big number, bad/good columns, red caveat box, steps), thin prose around.
2. Set the background on `@page`, not `body`, or page margins stay white.
3. Don't split callouts across pages: `break-inside: avoid`.
4. SVG for weasyprint only from simple primitives (rect, circle, path, line, polygon, text, gradients), no `filter`; weasyprint doesn't support `backdrop-filter`.
5. Slice: pages to PNG with headroom, fit each by height into a 1080×1350 canvas in the page background color. Make slide 1 a separate native 4:5 cover.

```css
@page { size: A4; margin: 18mm 16mm; background: #F4EFE6 }
h2 { break-before: page }
.callout, .cols, .pull, .cta { break-inside: avoid }
```

```bash
weasyprint longread.html longread.pdf
pdfinfo longread.pdf | grep -E "Pages|Page size"           # 595 x 842 pts
pdftotext longread.pdf - | grep -c '—'                      # 0
pdftoppm -r 200 -png longread.pdf pg                        # 10+ pages -> pg-01.png
```

```python
from PIL import Image; from pathlib import Path
BG, W, H = (244, 239, 230), 1080, 1350
for i, p in enumerate(sorted(Path(".").glob("pg-*.png")), 1):
    im = Image.open(p).convert("RGB"); s = H / im.height
    im = im.resize((int(im.width * s), H), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), BG); canvas.paste(im, ((W - im.width) // 2, 0))
    canvas.save(f"slide-{i:02d}.png")
```

## Verify
Page corner matches the background, not white:

```bash
python3 -c "from PIL import Image; print(Image.open('pg-01.png').getpixel((6,6)))"
```

No callout split; slide numbering matches pages.

## Don't
- Don't use small type on A4 meant for slicing: fitting A4 by height into 4:5 leaves side margins and small text is unreadable. Use large type or lay out dense pages separately.

## Evidence
A PDF document-carousel on LinkedIn and Telegram got 3,585 views; a 77-page handbook 8,099 total across platforms. An English PDF carousel was the best-reaching format on LinkedIn: about 1,387 impressions. This is format reach, not a comparison with manual layout.

## Related
- [Cover: AI draws only the background](carousels-cover-ai-background-only.md)
- [Rasterize px pages at -r 96](carousels-pdftoppm-96dpi.md)
- [Count clicks, not impressions](../analytics/analytics-clicks-not-impressions.md)
