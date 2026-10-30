---
id: carousels-cover-ai-background-only
title: Generate only the cover background with AI; set the title in code on top
section: carousels
lang: any
status: hypothesis
evidence: experience
tools: [image generator, HTML/CSS, weasyprint]
learn: ../../learn/en/09-carousels-slides.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
An image generator asked for "a cover with title X" mangles letters: garbage glyphs, stray strokes, mixed-up non-Latin scripts. You can only regenerate, and the text is not editable afterwards.

## Do
1. Prompt: background and mood only, vertical 4:5 or 2:3, "no text, no letters", empty zones top and bottom for text, your palette in words and HEX.
2. Crop: 1080×1350 for carousel slide 1, A4 (ratio 0.707) for the PDF cover.
3. In HTML on top: gradient scrim in the text zone, kicker, title, subtitle, footer with logo. Render with weasyprint.

```html
<style>
@page { size: 1080px 1350px; margin: 0 }
.c  { position: relative; width: 1080px; height: 1350px;
      background: url('bg.png') center/cover no-repeat; }
.scrim { position: absolute; inset: 0 0 40% 0;
      background: linear-gradient(180deg, rgba(244,239,230,.96), rgba(244,239,230,0)); }
.t  { position: absolute; top: 150px; left: 84px; right: 84px;
      font: 74px/1.05 Georgia, serif; letter-spacing: -2px; }
</style>
<div class="c"><div class="scrim"></div><div class="t">Title in code</div></div>
```

## Verify
No generator-made letter on the cover. The title is edited in HTML and re-rendered in seconds.

## Don't
- Don't let the generator draw in-story lettering (sign, handwritten note) either: overlay it in code or vector.

## Evidence
No own measurement. One background covers both the PDF cover and carousel slide 1.

## Related
- [Longread to PDF and carousel from one source](carousels-longread-to-carousel.md)
- [Rasterize px pages at -r 96](carousels-pdftoppm-96dpi.md)
