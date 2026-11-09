---
id: qa-picture-checks-warn-only
title: Run hook, flash, repeat and action checks on the mp4 as warnings, after calibrating them on your own verdicts
section: qa
lang: any
status: hypothesis
evidence: measurement
tools: [ffmpeg, Python, numpy]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-11-09
updated: 2026-11-09
contributors: [not-a-blogger]
---

## When
You want automatic checks against "static" and "monotonous" videos on the finished file: does the picture move in
the first 2 s, are there one-frame flashes, does a composition come back later, does anything act inside a scene
apart from the camera. Other kits ship these as pass/fail gates.

## Do
1. Run both tools on the final mp4 and read them as a list of seconds to look at:
   - `picture_checks.py`: hook (mean |Δ| of neighbouring frames over the first 2 s ≥ 0.5 of 255, every pair of steps
     ≥ 0.02) and pops (a frame ≥ 4/255 away from both neighbours while the neighbours are alike);
   - `scene_gate.py`: per scene, the residual after the best shift + scale (camera subtracted) and the share of
     seconds whose composition repeats one seen ≥ 6 s earlier.
2. Open the flagged timestamps on the contact sheet. A flagged pop is often an intended pulse, shake or film flicker;
   a flagged "camera-led" scene is often a word-by-word text reel where the motion is a few pixels.
3. Before trusting any threshold, calibrate: a TSV `path<TAB>good|bad` of your own videos with the person's verdicts.
   If the good and bad rows overlap, keep the check as a warning and never let it block a build.

```bash
python3 tools/qa/picture_checks.py output/final.mp4 --json qa/picture.json      # exit 0, warnings in JSON
python3 tools/qa/scene_gate.py output/final.mp4 --json qa/scene-gate.json --md qa/scene-gate.md
python3 tools/qa/scene_gate.py --calib my-verdicts.tsv --limit 60               # one row per video
```

## Verify
`qa/picture.json` and `qa/scene-gate.json` exist, every warning has a timestamp, and you looked at those frames on the
contact sheet before reporting. The QA status (`ready_for_user_preview` or yours) does not depend on these warnings.

## Don't
- Don't make any of these checks a gate or a pass/fail line in `qa/final-result.json`: on the author's videos they
  rejected approved reels.
- Don't tighten thresholds until the check "catches" a video you dislike; that only moves the overlap.
- Don't read a clean report as "the video is alive": a rejected video passed every check.

## Evidence
Calibration on 20 of the author's videos with the person's verdicts (12 approved, 2 mixed, 6 rejected; two long
videos measured on the first 60 s):
- Hook check: four approved videos failed it, three word-by-word text reels (mean |Δ| 0.46, 0.36, 0.17) and a 3D
  skit (0.37), while five of six rejected videos passed (0.56–7.76). The text reels move a word, a line or a
  cursor; on a 160 px thumbnail that is almost nothing. The checks separate a slide-like long video from canvas and 3D videos, not from approved text reels.
- Repeat share (≥ 6 s later): 0.31–0.44 on the same three approved reels against 0.50 on the long video rejected as
  "static" and 0.00–0.01 on five rejected shorts.
- Scene share without action (camera subtracted): 1.00 on the three approved reels and on the rejected long video;
  0.00–0.61 on rejected shorts.
- Pops: one each in 4 videos (three approved, one rejected); by eye all four were intended effects (ring pulse,
  frame shake, film flicker, brightness pulse). A synthetic one-frame flash is found every time (tests).
- A copy of a successful video on the same skeleton was rejected; the repeat check looks inside one video and
  cannot see repeats between videos, by design.
Status stays hypothesis: the tools work as described, but no threshold separated good from bad. Calibrate on yours.

## Related
- [Treat the motion metric as a hint](qa-motion-metric-is-a-hint.md)
- [Review the final contact sheet yourself](qa-contact-sheet-final.md)
- [Green QA is not approval](qa-green-is-not-approval.md)
