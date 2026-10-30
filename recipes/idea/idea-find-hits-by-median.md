---
id: idea-find-hits-by-median
title: Take ideas from niche hits selected by the author's median
section: idea
lang: any
status: proven
evidence: video-metric
tools: [yt-dlp, faster-whisper, ffmpeg]
learn: ../../learn/en/01-idea-hook-script.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Choosing the next idea. The candidate comes from your head or from news with no proven format.

## Do
1. Collect 50–90 authors in your niche (platform search, 10–20 queries).
2. Pull each author's video grid and compute the author's median views.
3. **Hit** = a video with ≥ 5× its author's median and ≥ 100k views.
4. Per hit: a 6-frame contact sheet, transcript, card (hook, format, presenter, shooting difficulty, CTA, reproducible yes/no).
5. Group hits by format; pick the simplest for your production.
6. Every new idea = news or own topic + a specific hit reference with its numbers.

```python
import statistics
def hits(videos_by_author, k=5, floor=100_000):
    out = []
    for author, vids in videos_by_author.items():
        med = statistics.median(v["views"] for v in vids)
        out += [v for v in vids if v["views"] >= max(k * med, floor)]
    return out
```

## Verify
Every idea in the plan links a reference hit with numbers. 24 h after publishing, compare the video with your own median, not with the hit.

## Don't
- Don't skip median normalisation: large accounts make every video look "big".
- Don't trust auto-selection blindly: label off-topic hits by hand.
- Don't treat correlation as cause.

## Evidence
- Sample: 92 candidates, 65 authors with enough videos, 115 hits by the "5 medians and 100k" rule, 106 downloaded.
- Presenter in hits: face 44, AI character 34, text and music only 17, voice-over 11. No face in 62 of 106.
- A video made in the format of someone else's hit: 212k Instagram views in one evening, against the account's usual 16–400.
- Limits: views come from rounded counters, no retention data. About 15 of 115 hits were off-topic everyday posts by the same authors. Grid collection is slow; profile APIs hit rate limits quickly.

## Related
- [Remake rhythm, not words](idea-remake-rhythm-not-words.md)
- [Everyday absurd and genre parody](idea-everyday-absurd.md)
- Example: [The TV showed an ad. The agent turned it off](../../examples/tv-no-ads/README.md)
