---
id: captions-grow-upward
title: Anchor karaoke to the strip bottom so wrapping grows upward
section: captions
lang: any
status: hypothesis
evidence: experience
tools: [CSS]
learn: ../../learn/en/06-sound-captions.md
added: 2026-10-23
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
A long line wraps to a second caption row and covers UI elements or bottom rows of cards.

## Do
1. Anchor the karaoke line container with `bottom: 0`, so wrapping grows upward.
2. Raise the caption strip to leave headroom (one video: up to 152 px from the bottom).
3. Keep the scene content's bottom edge above the strip's top edge at max row count.
4. Vertical: different geometry and platform UI at the bottom; check a frame with the UI overlay.
5. For short reels consider the opposite of a growing strip: 2–3 words per caption, one line, one object in frame. A hit series in the niche used exactly that (hypothesis: seen in another creator's series, not compared on our own videos).

```css
#karaoke { position: absolute; left: 0; right: 0; bottom: 152px; height: 0; }
#karaoke .kl { position: absolute; bottom: 0; width: 100%; text-align: center; }
```

## Verify
The longest line on a dry frame doesn't touch content; at 1080 height a three-row strip of 34 px occupies y 930–1057, everything else stays above 930.

## Don't
Don't anchor captions by `top`: wrapping then grows down into the content or off frame.

## Evidence
34 px karaoke in three rows occupied y 930–1057 of a 1080-high frame.
Geometry of one video, no outcome measured. To promote: count caption/content overlaps on the contact sheets of N videos with the bottom-anchored strip against the old top-anchored layout.

## Related
- [Caption colors and contrast](captions-colors-contrast.md)
- [Blink with color, not opacity](captions-blink-color-not-opacity.md)
- Example: [Whole course in 20 minutes (failed)](../../examples/course-retelling/README.md)
