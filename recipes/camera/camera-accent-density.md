---
id: camera-accent-density
title: Put camera accents on at most a third of the shots and never three push-ins in a row
section: camera
lang: any
status: hypothesis
evidence: experience
tools: [storyboard]
learn: ../../learn/en/05-camera-editing.md
added: 2026-10-27
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
Every shot opens with a push-in, a kick or a punch-in on a word. Each shot is fine alone; together the video pulses like one gesture repeated forty times, and the eye stops noticing the accents.

## Do
1. Before building, write the shot list as a table: `time | subject | action | camera`.
2. Count accents: kick (scale 1.55 → 0.94 → 1.0 in 0.17 s), snap push-in (+18–32 % in 0.25–0.35 s), whip pan, punch-in on a word. Accents ≤ ⅓ of the shots; the rest hold or move slowly (slow push 0.6–1.5 s, pull-out 0.8–2 s, pan to the next subject 0.5–0.9 s).
3. Never three push-ins in a row, even across cuts. Between two push-ins put a pull-out, a pan or a static shot.
4. After a push-in, come back out before the next push on the same subject: the next shot is a pull-out, a pan to a neighbouring subject, or a cut to another shot scale. A second push-in on the same subject at the same scale is not allowed.

```python
def density_check(shots):
    # shots: list of camera moves, e.g. ["push", "hold", "kick", "pull", ...]
    accents = {"kick", "push", "whip", "punch"}
    n_acc = sum(s in accents for s in shots)
    run = max_run = 0
    for s in shots:
        run = run + 1 if s == "push" else 0
        max_run = max(max_run, run)
    return n_acc <= len(shots) / 3 and max_run <= 2
```

## Verify
- Shot table: accents ≤ ⅓ of rows, longest run of consecutive push-ins ≤ 2, no row "push on X" directly after "push on X".
- After render, step through the contact sheet: a slow push on a still subject does not cure stillness; action in the frame does.

## Don't
- Don't fix a static shot by adding another push-in; change what happens in the frame.
- Don't apply the rule per scene file only: count across the whole video, cuts included.

## Evidence
Rule set from the "density" section of the camera-moves skill (own words after a public MIT motion guide): an author's 102 s video with 48 push-ins, all inward, was judged by its own author as "not smooth at all" although each shot alone was fine. Not yet measured on this kit's videos against viewer metrics.

## Related
- [Camera-moves skill, section «Плотность»](../../starter/.agents/skills/camera-moves/SKILL.md#плотность)
- [Change shot scale with a cut, not a zoom](camera-scale-change-not-zoom.md)
- [Don't mask a static frame with a slow push-in](camera-no-ken-burns.md)
