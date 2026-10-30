---
id: brand-palette-in-root
title: Keep the palette in :root of one CSS file and read it from the timeline via getComputedStyle
section: brand
lang: any
status: proven
evidence: measurement
tools: [CSS, GSAP]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Colors are scattered as literals across scenes, animation scripts and generators. Nobody chose the palette: it came from the first video and gets copied into every next one. Rebranding means touching every file.

## Do
1. All colors, radii, shadows and easings in `:root` of one theme file.
2. Animation scripts and scene generators hold no color literals: they read tokens from CSS.
3. Theme change = replace one `:root` block. Build the same probe in two or three themes and pick by eye.

```css
:root {
  --bg: #ffffff; --ink: #1a2023; --muted: #536067;
  --acc: #425319; --acc-hi: #d6ff43;
  --radius: 12px; --shadow: 0 22px 54px -24px #26322855;
  --ease: cubic-bezier(.16, 1, .3, 1);
}
```

```js
const css = getComputedStyle(document.documentElement);
const ACC_HI = css.getPropertyValue('--acc-hi').trim();
gsap.to('.word.active', { backgroundColor: ACC_HI, duration: .3 });
```

```bash
# color literals outside the theme file: must be empty
grep -rnoE '#[0-9a-fA-F]{6}\b' scenes/ scripts/ | grep -v theme.css
```

## Verify
grep finds no HEX colors outside the theme file; replacing `:root` recolors the whole video without touching scenes.

## Don't
- Don't expect tokens to control raster images (photos, generated backgrounds): match those to the palette via the prompt.

## Evidence
13 of 14 video projects turned out to share one black palette nobody chose: copied from the first "Apple-like" video, then file to file. After moving the palette to `:root`, one probe was built in three themes (black, warm paper, brand) and brand was chosen.

## Related
- [Accent as fill only](brand-accent-fill-only.md)
- [Content separate from theme](../carousels/carousels-content-theme-split.md)
- Example: [A hook that blocks a dangerous command](../../examples/hook-vertical-from-long/README.md)
