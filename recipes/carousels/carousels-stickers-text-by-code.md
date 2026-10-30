---
id: carousels-stickers-text-by-code
title: Render sticker text in code with font size auto-fit to width
section: carousels
lang: any
status: hypothesis
evidence: experience
tools: [Playwright, SVG, cwebp]
learn: ../../learn/en/09-carousels-slides.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Generated stickers arrive with typos and foreign logos; each new caption means a new generation. A long line in fixed size overflows the plate.

## Do
1. Sticker background and frame in SVG, text as an HTML layer, render in a browser with a transparent background.
2. Shrink the big line's font until it fits the target width; set a ready flag.
3. Screenshot only after the fit.
4. New sticker = one row in the data table (caption, plate, small line, icon, number). Don't draw other companies' marks: use a number or your own icon.
5. Telegram upload via the @Stickers bot: `/newpack`, send PNG as a file, not a photo, an emoji after each sticker, finish with `/publish` and a 100×100 icon.

```js
// sticker page 512x512, background transparent
const b = document.querySelector('.big');
let fs = 62; const maxW = 284;
while (b.offsetWidth > maxW && fs > 24) { fs -= 1; b.style.fontSize = fs + 'px'; }
document.body.dataset.ready = fs;   // fit done
```

```js
// render.mjs (Playwright): transparent PNG 512x512
const page = await browser.newPage({ viewport: { width: 512, height: 512 }, deviceScaleFactor: 1 });
await page.goto('file://' + path.resolve('out/sticker-01.html'));
await page.waitForFunction(() => document.body.dataset.ready);
await page.screenshot({ path: 'out/sticker-01.png', omitBackground: true });
```

```bash
cwebp -q 90 sticker.png -o sticker.webp
```

## Verify
Sticker exactly 512×512, transparent background, no line touches the plate edge on the longest text.

## Don't
- Don't rely on auto-fit for very long phrases: at the lower bound break the line manually (`\n`) or shorten the text.

## Evidence
Pack of 8 stickers 512×512: WEBP 33–38 KB each. Big-line size fits from 62 px down to 24 px in a 284 px field.

## Related
- [Stickers in a layer outside the camera](../brand/brand-stickers-outside-camera.md)
