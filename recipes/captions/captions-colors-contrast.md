---
id: captions-colors-contrast
title: Dim inactive caption words and check contrast on every theme
section: captions
lang: any
status: proven
evidence: measurement
tools: [CSS]
learn: ../../learn/en/06-sound-captions.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Karaoke colors were picked on a dark theme and the video moved to a light one: grey inactive words give 1.9–2.6:1 contrast and are unreadable; accent-colored text on light also gets lost.

## Do
1. Dark background: base words white at 52% alpha, active word in accent color.
2. Light background: darken inactive words to dark grey; check contrast.
3. Keep colors in `:root`; the timeline reads them via `getComputedStyle`; switch theme with one CSS block.
4. On dark ground make the header light from frame zero.

```css
:root { --kar-base: rgba(255,255,255,.52); --kar-active: var(--accent); }
:root[data-theme="light"] { --kar-base: #79857f; }
```

```js
const c = getComputedStyle(document.documentElement).getPropertyValue("--kar-active").trim();
```

## Verify
A contrast check (WCAG calculator or scene linter) gives no warnings on both themes.

## Don't
Don't use a bright accent (lime, yellow) as text color on light background; use it as fill only.

## Evidence
- Grey karaoke from the dark theme on the light one: 1.9–2.6:1 and 30 checker warnings; darkening inactive words cleared them.
- Olive text on dark background: 1.99:1.

## Related
- [Captions grow upward](captions-grow-upward.md)
- [Font and caption burn-in](captions-font-and-burn.md)
