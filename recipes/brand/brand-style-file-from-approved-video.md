---
id: brand-style-file-from-approved-video
title: Write STYLE.md from the video the person approved, and keep the style, not the scenes
section: brand
lang: any
status: hypothesis
evidence: viewer-feedback
tools: [CSS]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-11-08
updated: 2026-11-08
contributors: [not-a-blogger]
---

## When
A series starts: one video was approved and the next ones should look like the same show. Without a written style the
agent copies the previous project folder, and with it the old palette, old scenes and old mistakes.

## Do
1. Only after the person approved a video, write `STYLE.md` next to the series. Link the approved mp4 and its SHA256.
2. Write down what repeats in every episode:
   - palette as CSS tokens (see [palette in :root](brand-palette-in-root.md));
   - fonts with their licenses;
   - composition: where the subject sits, caption position, safe margins;
   - motion: durations, easing, camera scale limits;
   - captions: words per line, colors, outline;
   - sound: music source, SFX on cuts, loudness target;
   - what the series never does.
3. Add the person's own words about what they liked and what they rejected, with dates.
4. Keep scene layouts, jokes and hooks out of `STYLE.md`. Each episode gets a new story and new staging inside the same
   style.
5. Start every new episode by reading `STYLE.md`, not by copying the previous episode's folder.

```markdown
# STYLE.md: <series>
Approved reference: output/ep01.mp4 (sha256 …), approved 2026-…
Palette: --ink #… --accent #… (accent as fill only)
Fonts: … (OFL)
Captions: 2–3 words, 330 px from bottom, …
Motion: cuts every 2–4 s, camera scale ≤ 1.05 at rest
Never: dark theme by default, mascot more than once, …
Person said: "…" (date)
```

## Verify
The next episode is built without copying files from the previous one, and a side-by-side contact sheet of both shows
the same palette, type and caption position with different scenes.

## Don't
- Don't write `STYLE.md` before approval: a style taken from a rejected draft locks in what was wrong.
- Don't put a scene template into the style: a new episode on the old scene skeleton was rejected as slop.

## Evidence
- A dark theme sat in every video because the agent copied previous projects; it came from copy-paste, not from a
  decision, and was replaced by the brand palette once the person asked why.
- An episode built as a copy of a successful one on the same scene skeleton was rejected by the person as slop.
- Both are feedback cases, no measurement. To promote: count person-rejected episodes in a series built from
  `STYLE.md` against one built by copying folders.

## Related
- [Keep the palette in :root](brand-palette-in-root.md)
- [Don't repeat your own hit](../idea/idea-no-repeat-own-hit.md)
