# Carousels, cards, covers, stickers

Swipe cards 1080×1350, A4 PDF sliced into a carousel, covers and stickers. Pipeline: HTML/CSS → weasyprint → PDF → pdftoppm → PNG. Format: [recipe template](../../templates/recipe.md).

| Recipe | Status | Lang | Gist |
|---|---|---|---|
| [carousels-content-theme-split](carousels-content-theme-split.md) | hypothesis | any | Cards as data tuples, look in one theme CSS with a shared class set. |
| [carousels-cover-ai-background-only](carousels-cover-ai-background-only.md) | hypothesis | any | AI draws only the background; title, scrim, footer in HTML. |
| [carousels-local-full-fonts](carousels-local-full-fonts.md) | hypothesis | any | Full local woff2 via `file://`; check glyphs with fontTools. |
| [carousels-longread-to-carousel](carousels-longread-to-carousel.md) | hypothesis | any | One A4 PDF, slice pages into 1080×1350 slides. |
| [carousels-pdfinfo-page-size](carousels-pdfinfo-page-size.md) | proven | any | After render expect `810 x 1012.5 pts`; A4 means `@page` was dropped. |
| [carousels-pdftoppm-96dpi](carousels-pdftoppm-96dpi.md) | proven | any | `pdftoppm -r 96` for px pages; -r 72 gives 0.75× size. |
| [carousels-prerender-gate](carousels-prerender-gate.md) | hypothesis | any | Hard gate on card data, then `pdftotext` dash check on the PDF. |
| [carousels-stickers-text-by-code](carousels-stickers-text-by-code.md) | hypothesis | any | Sticker text in HTML, font auto-fit 62→24 px, Playwright transparent PNG. |
