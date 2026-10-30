---
id: qa-word-sync-check
title: Check overlays against word timestamps: ±0.3 s per named noun, a cut every 3 s, a free caption zone
section: qa
lang: any
status: hypothesis
evidence: measurement
tools: [Python, ffmpeg, pymorphy3]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-26
updated: 2026-10-26
contributors: [not-a-blogger]
---

## When
The build has word-level timestamps (from TTS alignment or ASR) and a timeline of overlays (plates, phone mock-ups,
windows, captions), and nobody checks whether a plate shows up when its word is spoken, whether a shot lasts too long,
or whether a plate covers the captions. Frame review catches these only by luck.

## Do
Run four checks on the timeline, plus the final mp4 for cuts:

1. **Named noun on screen within ±0.3 s.** For each overlay with text, lemmatize its words (for Russian: `pymorphy3`;
   spell numerals as digits so "forty" matches "40") and find the spoken line that matches most of them, the
   overlay's title first. Late = overlay appears more than 0.3 s after its first spoken noun. Early = more than 0.3 s
   before any of its words.
2. **A new shot at least every 3 s.** Gaps between shot starts on the timeline; separately, `ffmpeg scdet` on the
   mp4 as a cross-check.
3. **Caption zone is free while a caption is on screen.** Intersect overlay boxes with the caption box. Use your
   renderer's real caption box; the source rule puts captions at 56–74 % of height, ours sit at 76–83 %.
4. **The old text is gone before the new one.** A caption must not appear late because the previous one is still
   held; two overlays that overlap in time *and* in the frame are a failure; overlapping in time only is a warning.

```python
import re, subprocess
def cuts_from_mp4(mp4, thr=8):            # cross-check for check 2
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", mp4, "-an",
                          "-vf", f"scale=270:480,scdet=threshold={thr}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return [float(t) for t in re.findall(r"lavfi\.scd\.time: ([0-9.]+)", err)]

def long_shots(cuts, duration, max_gap=3.0):
    pts = sorted({0.0, *cuts, duration})
    return [(a, b) for a, b in zip(pts, pts[1:]) if b - a > max_gap]

def late_or_early(overlay_start, first_word_start, first_noun_start, tol=0.3):
    if overlay_start - first_noun_start > tol: return "late"
    if overlay_start - first_word_start < -tol: return "early"
    return "ok"
```

Write a report with one table per check. Checks 1 and 2 (±0.3 s, a shot every 3 s) are chosen heuristics, so they
only warn (see [QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md)); exit with code 1 on failures of checks 3 and 4.
Also downgrade to a warning, not a failure:
in-world screens (visible only when the camera looks at them), the hook frame (an object from frame 0 is
intentional), the final card (it repeats what was said), a Latin title spoken in transliteration, and groups of
plates that build a diagram together.

## Verify
- Open two or three frames at the reported times: a "caption covered" failure must show the plate over the caption.
- The scdet cross-check should miss few timeline cuts; if it misses many, trust the timeline.
- Exit code 0 only when every check 3–4 failure has been fixed or consciously accepted; warnings from checks 1–2 are
  listed for the person.

## Don't
- Don't treat a green run as approval; it checks timing and geometry, not whether the video is watchable.
- Don't trust scdet alone on dark motion graphics: it misses changes made by motion rather than cuts.
- Don't trust frame-based detection of plates in 3D scenes: in our runs it hit mostly background.
- Don't run heavy steps (ASR, render) from this check; it reads existing artifacts.

## Evidence
Origin: rules inspired by a breakdown of the Kylo AI format (YouTube yVCc0NbZVbQ), our own implementation. Run on
three finished vertical skits (45 s, 46 s, 3:17) on 2026-10-26:
- 45 s skit: 8 failures. Two plates appear 0.5 and 0.9 s after their noun (anchored to the punch word, not the first
  noun); six shots of 3.1–5.2 s.
- 46 s skit: 3 failures (one plate 0.31 s early, two shots of 3.2 and 4.1 s).
- 3:17 explainer: 25 failures. Confirmed on frames: a phone mock-up covers the caption twice (14.0 s, 104.6 s) and a
  plate lands on a mini-map label. 13 shots longer than 3 s, most of them filled with plates appearing one by one.
- False positives seen: a phone matched to a word from the previous line; root-related words not matched
  ("call" / "called").
- scdet at threshold 8 missed 2 of 17 timeline cuts on the first skit (same character, similar framing), 0 on the
  second. On a dark motion-graphics reel it reported 19 s without a cut although the frame kept changing.
- Frame-based plate detection in the caption band: precision 4–14 % against the timeline on 3D scenes.
- Whether fixing these failures changes retention is not measured: status hypothesis.

## Related
- [Contact sheet of the final file](qa-contact-sheet-final.md)
- [Still lint](qa-still-lint.md)
- [Frame fill on the mp4](qa-frame-fill-mp4.md)
- [Word-anchored animation](../assembly/assembly-word-anchored-animation.md)
- [Green is not approval](qa-green-is-not-approval.md)
