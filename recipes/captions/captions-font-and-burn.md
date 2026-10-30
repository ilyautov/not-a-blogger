---
id: captions-font-and-burn
title: Check font glyphs and burn captions as PNG frames without libass
section: captions
lang: any
status: hypothesis
evidence: experience
tools: [ffmpeg, Pillow]
learn: ../../learn/en/06-sound-captions.md
added: 2026-10-23
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
- The ffmpeg build lacks libass; the `subtitles` filter is unavailable.
- A web-font subset (e.g. Cyrillic) lacks "-" and "?"; a display font's "%" at large size renders as a fallback-font stub.
- Ink of a narrow display font overflows its line box; a caption under a big number slides under it.

## Do
1. Run `ffmpeg -filters | grep subtitles`. If empty, render captions as transparent PNG frames and `overlay` them.
2. Fit line width by the real font metrics.
3. Before render, check every needed character exists in the font file; set units next to big numbers in a monospace font.
4. Position a caption under a big number absolutely, offset `1.02 × font-size + 26` px.

```python
from fontTools.ttLib import TTFont
cmap = TTFont("font.ttf").getBestCmap()
missing = [ch for ch in "-?%«»—…" if ord(ch) not in cmap]
print("missing glyphs:", missing)
```

```bash
ffmpeg -i video.mp4 -framerate 30 -i subs/%05d.png -filter_complex "[0][1]overlay=0:0" -c:a copy out.mp4
```

## Verify
The missing-glyph list is empty; frames with percents and question marks show no boxes or stubs.

## Don't
Don't skip the glyph check even when loading the full font (not a subset); it usually helps, still verify.

## Evidence
- Display-font ink overflowed the box by ~0.2 of font size up and down.
- The "%" stub appeared at 100+ px.
Overflow figures come from one font on one video; no count of defects avoided. To promote: run the glyph check on N scripts and count missing glyphs and box overflows found before render versus after.

## Related
- [Caption colors and contrast](captions-colors-contrast.md)
- [Final contact sheet](../qa/qa-contact-sheet-final.md)
