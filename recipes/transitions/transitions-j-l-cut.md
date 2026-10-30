---
id: transitions-j-l-cut
title: Bridge scenes with sound — J-cut before the picture, L-cut after
section: transitions
lang: any
status: hypothesis
evidence: experience
tools: [ffmpeg]
learn: ../../learn/en/05-camera-editing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Sound and picture are cut at the same point; every cut feels like a break.

## Do
- **J-cut:** next scene's sound starts 0.3–0.5 s before its picture. The sound must be recognisable, or the viewer won't link it to the shot.
- **L-cut:** previous scene's sound runs 0.3–1.5 s past the cut, fading out over the last 0.5 s.

```bash
# J: sound B starts 0.45 s before the cut at 12.0 s
ffmpeg -i a.wav -i b.wav -filter_complex \
 "[1]adelay=11550|11550[b];[0][b]amix=inputs=2:normalize=0" mix.wav
# L: tail of A after the cut, 0.5 s fade
ffmpeg -i a.wav -af "afade=t=out:st=12.9:d=0.5" a_tail.wav
```

## Verify
On the timeline B's sound leads the cut by no more than 1 s; A's tail ends without a click.

## Don't
- Don't lead by more than 1 s: it reads as a sync error.
- Don't lay a loud tail over a loud B start: it turns to mush.

## Evidence
No own measurements; values from a camera-moves reference.

## Related
- [Smash cut](transitions-smash-cut.md)
- [SFX by meaning](../sound/sound-sfx-by-meaning.md)
