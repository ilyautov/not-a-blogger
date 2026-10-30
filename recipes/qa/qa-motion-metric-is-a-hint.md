---
id: qa-motion-metric-is-a-hint
title: Treat the motion metric as a hint with one alarm, not as a quality gate
section: qa
lang: any
status: proven
evidence: measurement
tools: [ffmpeg, Python, numpy, OpenCV]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-27
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
You are tempted to gate publishing on a motion number: "fast_ratio below X = slop, above X = fine". A viewer said a video "has no motion design", and the metric looks like the obvious automatic check.

## Do
1. Run `motion_gate.py` on the finished mp4 and read only the alarm: `active_ratio < 0.10` means almost no frame pair inside shots has even 1 % of the frame moving. Exit code 2 = go and look at the video.
2. Use the rest of the report (dead shots, worst 30-second window, per-shot table) as a map of where to look, not as a score.
3. Judge meaning, voice and rhythm by eye and ear: a 20-second trial cut shown to a person before building the whole video.
4. Before trusting any new metric, calibrate it: a TSV `path<TAB>good|bad` of your own videos with human verdicts, then `--calib`. The tool prints "separates" or "does NOT separate".

```bash
python3 tools/qa/motion_gate.py output/final.mp4 --json qa/motion.json --md qa/motion.md
echo $?                      # 2 only for the "dead as a slide deck" alarm
python3 tools/qa/motion_gate.py --calib my-verdicts.tsv     # does the metric separate your good from your bad?
```

## Verify
`qa/motion.json` has `verdict: info` and the per-shot table shows the shots you expected to be still (a held frame under a number) and no others. If the calibration line says "does NOT separate", the metric must not appear in a pass/fail rule.

## Don't
- Don't promise that a motion metric catches "slop": it measures changed pixels, not whether the video is worth watching.
- Don't turn stillness into a second alarm. The rhythm "stop → jump → stop" is good; a slow 6 % camera push over 5 s is counted as still and that is correct.
- Don't raise the alarm threshold to make it fire more often; it rests on one negative example.

## Evidence
- Calibration on 18 of the author's videos with human verdicts (approved / rejected / mixed): neither `fast_ratio` (frame difference ≥ 9/255) nor `active_ratio` (≥ 1 % of the frame moving) separated the groups. Two rejected business explainers moved more than two approved everyday-situation shorts; the author's best-received long-form (`active_ratio` 0.161) was nearly as still as the long-form rejected as "static" (0.078).
- Thresholds 6, 9 and 12 for "fast" give the same ordering, so the non-separation is not a threshold choice.
- The single alarm (`active_ratio < 0.10`) is set between the one rejected-as-static video and its nearest approved neighbour: one negative example, hence "hint", not "gate".

## Related
- [Green QA is not approval](qa-green-is-not-approval.md)
- [Stillness lint with camera off](qa-still-lint.md)
- [Measure frame fill on the mp4](qa-frame-fill-mp4.md)
- [Break down the reference before a remake](../idea/idea-breakdown-reference-before-remake.md)
