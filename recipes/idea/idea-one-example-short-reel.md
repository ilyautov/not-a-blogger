---
id: idea-one-example-short-reel
title: Keep a reel under 40 s, one example, punchline before methodology
section: idea
lang: any
status: hypothesis
evidence: viewer-feedback
tools: [ffprobe]
learn: ../../learn/en/01-idea-hook-script.md
added: 2026-10-23
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
The draft reel packs a whole experiment: methodology, accuracy tables, several blocks of numbers with caveats. An honest breakdown wants to be told in full (how you tested, how many tasks, error margin); in a reel this becomes a lecture, and strong gags drown between tables.

## Do
1. One example = one video. Other examples become the next videos.
2. Punchline or funniest result in the first seconds; explanation after.
3. Methodology, caveats and tables go to the caption or a pinned comment.
4. Length ≤ 40 s. Estimate runtime from voice-over durations before editing: roughly N/4 lines for N seconds.
5. No tables, bar charts, or small prompt text in frame.
6. Remove model names the viewer won't recognise from speech.

```bash
# total voice-over take duration, seconds
for f in takes/*.wav; do ffprobe -v error -show_entries format=duration -of csv=p=0 "$f"; done | paste -sd+ - | bc
```

## Verify
Retell the video in one sentence; if it contains "and also", it is two videos. The first 5 s show the result. Under 40 s, no table or bar chart in the video.

## Don't
- Don't apply this to the open-loop genre: a delayed-payoff hit can run 139 s (price in the hook, "three catches", answer 80 s later) with one question held open.
- Don't treat length as the verdict: the 40 s cap guards against lectures, not length as such.

## Evidence
- Rejected video: 2:11 long, methodology explained from 0:08 to 0:19 before the first funny example, half of the frames were tables and bars. Approver's verdict: "everything is very bad… from the meaning of the visuals to retention". 11 lines of 3.5 s didn't fit a 40 s video.
- In a sample of 102 viral Reels the median length was 63.2 s and 28 ran longer than 90 s: the cap is about one example per video, not a length rule. No own A/B of a 40 s cut against the long one.

## Related
- [Open loop and delayed payoff](../hooks/hooks-open-loop-payoff.md)
- [Script before build](idea-script-before-build.md)
- [Result at 0.0 s](../hooks/hooks-result-in-first-second.md)
- Example: [Asked the AI to free my Friday](../../examples/free-friday/README.md)
