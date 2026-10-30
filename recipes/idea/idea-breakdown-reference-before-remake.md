---
id: idea-breakdown-reference-before-remake
title: Break the reference down per second and compare it with the remake before judging the remake
section: idea
lang: any
status: hypothesis
evidence: measurement
tools: [ffmpeg, Python, numpy, librosa]
learn: ../../learn/en/01-idea-hook-script.md
added: 2026-10-27
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
You remake a hit second by second, keep its cut points and length, and the result still feels flat next to the original. You suspect you need more cuts.

## Do
1. Run `breakdown.py` on the reference you already have on disk, then with `--compare` on your remake. Read the side-by-side table: cuts per 10 s, shot lengths, `fast_ratio`, moving area, cuts on the beat.
2. Look at `heat.jpg` of the reference: red = pixels that changed within the shot. If every shot is red across the frame, the camera (or the subject) drifts continuously inside the shot.
3. If the cut counts match but the reference `fast_ratio` is several times yours, fix the drift inside the shot (a continuous slow move on every plan: push, slide, parallax), not the number of cuts.
4. Keep the reference and its frames out of public repositories; the breakdown folder is for your eyes.

```bash
python3 tools/qa/breakdown.py ref.mp4 --compare output/final.mp4 --out qa/breakdown
sed -n '/| | reference | remake |/,/^$/p' qa/breakdown/breakdown.md
```

## Verify
In `qa/breakdown/breakdown.md` the remake row for `fast_ratio` is within the same order as the reference, and `heat.jpg` under `compare/` shows motion in every shot, not only around the cuts.

## Don't
- Don't add cuts to catch up on motion: the reference moved inside the shots, not between them.
- Don't reupload or republish the reference; the breakdown exists so you can rebuild the rhythm with your own footage.
- Don't read the beat-fit share without its "chance" column: on a dense grid random cuts also land on half beats.

## Evidence
- One measured pair (a 37-second vertical remake of a 3D-voxel hit): cut counts matched the reference within one cut, but the reference camera drifted inside every shot with `fast_ratio` 0.76 while the remake stood still at 0.09. The remake's moving area per shot was 5 %, the reference's covered most of the frame.
- One pair is not a rule; hence status hypothesis. Add your own pairs.

## Related
- [Remake a hit second by second in your own words](idea-remake-rhythm-not-words.md)
- [Treat the motion metric as a hint](../qa/qa-motion-metric-is-a-hint.md)
