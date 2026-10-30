---
id: slides-html-deck-with-pdf-backup
title: Present the HTML deck in a browser; build the PDF backup from slide screenshots
section: slides
lang: any
status: hypothesis
evidence: experience
tools: [HTML/CSS, Playwright, Pillow, pdfinfo]
learn: ../../learn/en/09-carousels-slides.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
An agent-built HTML deck beats pptx (animations, own font, live blocks), but the venue may lack the right browser or network, and print-to-PDF breaks JS-switched slides.

## Do
1. Main show: the HTML file full screen in a browser, arrows/space/click to advance. Inline all assets (base64 images, local fonts) so it works offline.
2. Backup: walk the deck automatically, screenshot each slide at 1280×720, merge into a PDF. Wait for transitions to finish, or half-transparent frames land in the PDF.

```python
from playwright.sync_api import sync_playwright
from pathlib import Path
from PIL import Image
out = Path("render"); out.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.goto(Path("deck.html").resolve().as_uri())
    n = pg.locator(".slide").count()
    for i in range(n):
        pg.wait_for_timeout(500)                 # opacity transition .35 s + margin
        pg.screenshot(path=out / f"s{i+1:02d}.png")
        pg.keyboard.press("ArrowRight")
    b.close()
imgs = [Image.open(f).convert("RGB") for f in sorted(out.glob("s*.png"))]
imgs[0].save("deck.pdf", save_all=True, append_images=imgs[1:], resolution=72)
```

```bash
pdfinfo deck.pdf | grep -E "Pages|Page size"      # N pages, 1280 x 720 pts
```

## Verify
PDF page count = slide count in HTML; no page shows a half-transparent transition frame.

## Don't
- Don't ship the screenshot PDF as a reading copy: text isn't selectable or searchable. Use print CSS for that.

## Evidence
18-slide deck: HTML about 30 KB, screenshot PDF backup 18 pages 1280×720 pt, about 1 MB. No viewer measurement of HTML vs pptx.

## Related
- [Print version via @media print](slides-print-css.md)
- [Check the deck PDF with a contact sheet](slides-check-pdf.md)
