---
id: idea-five-beat-skeleton
title: Lay the script out in five timed beats, with a timestamped hero as a device
section: idea
lang: any
status: hypothesis
evidence: measurement
tools: []
learn: ../../learn/en/01-idea-hook-script.md
added: 2026-10-26
updated: 2026-10-26
contributors: [not-a-blogger]
---

## When
A script for a short skit or explainer is a list of lines with no shape: the hook, the reveal and the call to action
land wherever the dialogue happens to put them.

## Do
1. Split the script into five beats before writing lines. Timings for a skit of 45 s or less:

   | beat | job | time |
   |---|---|---|
   | 1. Hook | result, scandal or intrigue; context comes 3–5 s later | first line at 0.0 s |
   | 2. The mistake everyone makes | what the hero asked for, what anyone would do | 3–10 s |
   | 3. What actually happened | the consequence with one number per shot | 10–25 s |
   | 4. Steps | three escalation steps in a skit; 3–5 tips only in a how-to | 25–38 s |
   | 5. Twist or question | a twist, a question to the viewer and the comment keyword | 38–45 s |

2. For a 65–90 s explainer the same beats stretch to 0–5 / 5–20 / 20–45 / 45–75 / last 5–10 s. Use that only when the
   format really needs the length (see Don't).
3. Count words: the source format targets 2.4–2.7 words/s. Measure your own pace first (step below) and write to it;
   don't raise the pace by speeding up a cloned voice, shorten lines instead.
4. If the trouble grows over time, give the hero a timestamp plate: "DAY 1 — 18:04" → "NIGHT" → "DAY 3". Put it on the
   cut that opens the beat, never before the first spoken line.
5. Write a two-column table next to the script: line → what is on screen at that moment. Beat 3 must have a number
   on screen, beat 5 must have the keyword on screen.

```python
# measure words/s of your finished videos: timing.json with lines[].words[] {w, start, end}
import json, sys
for f in sys.argv[1:]:
    L = json.load(open(f))["lines"]
    n = sum(len(l["words"]) for l in L)
    speech = sum(l["end"] - l["start"] for l in L)
    print(f, f"{n / speech:.2f} w/s in speech, {n / L[-1]['end']:.2f} w/s overall")
```

## Verify
- Each beat starts inside its window (±1 s) in the voice timing; the first word is at 0.0–0.45 s.
- Beat 5 contains a question mark and the keyword, both in speech and on screen.
- Swap beats 2 and 3: if the story still reads, beat 2 is not a mistake, it is filler.

## Don't
- Don't let the skeleton push a skit past 45 s or move the hook later than 0.0 s: in our runs a slow intro was
  rejected twice ("the opening is weak"), and a 2:11 reel with methodology up front was rejected as a whole.
- Don't turn beat 4 into a list of tips inside a comedy skit: escalation, not advice.
- Don't copy the calm "instructor" tone of the source format if your channel is absurdist; the beats are tone-neutral.
- Don't put the timestamp plate over the subtitle zone.

## Evidence
- Origin: inspired by a breakdown of the Kylo AI format (YouTube yVCc0NbZVbQ), written in our own words; their
  production technique is not used.
- Our pace, measured on 16 finished skits (41–47 s, dialogue, cloned and live voices): 1.8–2.3 words/s over the whole
  video, 2.0–2.6 inside speech, 80–100 words per 45 s. That is below the source's 2.4–2.7; the effect of a faster
  pace on retention is not measured.
- The five-beat split itself has not been tested on a published video of ours yet: status hypothesis.

## Related
- [Result in the first second](../hooks/hooks-result-in-first-second.md)
- [Reel under 40 s, one example](idea-one-example-short-reel.md)
- [Script before build](idea-script-before-build.md)
- [Keyword in comments](../cta/cta-codeword-in-comments.md)
- [Don't speed up the clone](../voice/voice-no-speedup-clone.md)
