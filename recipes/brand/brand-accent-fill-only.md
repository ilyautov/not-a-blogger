---
id: brand-accent-fill-only
title: Use a bright brand color only as fill; add a dark shade for accent text
section: brand
lang: any
status: proven
evidence: measurement
tools: [CSS]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
An acid brand color (lime, yellow, mint) works as a patch and fails as letters. An accent word in it on a light background is nearly unreadable in a frame or card, especially on a phone.

## Do
1. Split the accent into two tokens:
   - `--acc-hi`: bright color, fills only (markers, active-word backgrounds);
   - `--acc`: dark shade of the same hue for text.
2. Bright color as text only on a dark plate.
3. Compute contrast for each pair.

```css
:root {
  --ink:    #1a2023;   /* body text */
  --acc-hi: #d6ff43;   /* lime: fill */
  --acc:    #425319;   /* olive: accent text on light */
  --plate:  #111b21;   /* dark plate: lime allowed as text */
}
.word.active { background: var(--acc-hi); color: var(--ink); }
.kicker      { color: var(--acc); }
.plate .num  { background: var(--plate); color: var(--acc-hi); }
```

```bash
python3 -c "
def L(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    c=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return .2126*c[0]+.7152*c[1]+.0722*c[2]
a,b=L('#d6ff43'),L('#ffffff'); print(round((max(a,b)+.05)/(min(a,b)+.05),2))"
```

## Verify
Every text/background pair is ≥4.5:1 for small text and ≥3:1 for large.

## Don't
- Don't use the bright color for small text on light backgrounds. For very large hero numbers kept bright for recognition, add a dark outline or shadow.

## Evidence
Lime `#d6ff43` on white: 1.15:1. Olive `#425319` on white 8.46:1, on lime 7.35:1. Lime on the dark plate `#111b21`: 15.17:1.

## Related
- [Palette in :root](brand-palette-in-root.md)
