---
id: analytics-compare-in-equal-slots
title: Compare styles and topics only between videos in the same upload slots, at the same age after publishing
section: analytics
lang: any
status: proven
evidence: video-metric
tools: [yt-dlp]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-28
updated: 2026-10-29
contributors: [not-a-blogger]
---

## When
You want to say "style A doesn't work" or "topic B wins" from your own view counts, and the videos went out on different days, in different upload positions or at different ages.

## Do
1. For every video record: platform, publish time, upload day (Pacific time for YouTube, UTC for TikTok), slot number that day.
2. Mark the slots you compare in: on the observed channel YouTube 1–3 and TikTok 1–5 got views and later slots did not (see [first three slots](../publishing/publishing-first-three-slots.md); the cause is a hypothesis). Measure where the drop is on your own channel, and drop every video outside those slots from the comparison.
3. Compare at equal age: take every video's views the same number of hours after **its own** publish time (for example 24 h and 48 h), not at one shared snapshot. Two videos published the same morning and evening differ by 12 h, which matters most in the first 24–48 h. Prefer pairs from the same day and comparable slots on top of that, so day and slot effects are also held equal.
4. Report the comparison with its n. Fewer than 3–5 videos per side in the compared slots: write "not enough data", not a verdict.
5. Keep the raw snapshot (JSON) and the table next to the conclusion, so the next person can redo the cut.

```python
LIVE = {"youtube": 3, "tiktok": 5}          # observed on one channel; re-measure on yours
AGE_H = 24                                    # views read AGE_H hours after each video's own publish time
rows = [r for r in rows if r["slot"] <= LIVE[r["platform"]] and r.get(f"views_{AGE_H}h") is not None]
by_day = {}
for r in rows:
    by_day.setdefault((r["platform"], r["day"]), []).append(r)
pairs = {k: v for k, v in by_day.items() if {"A", "B"} <= {r["style"] for r in v}}
```

## Verify
Every claim "A beats B" cites day(s), platform, slots, the age in hours after publishing at which views were read, and n for both sides. Rerun on the raw snapshot gives the same medians.

## Don't
- Don't divide views by age to compare videos of different days: a short gets almost all of its views in the first 24–48 h, so per-hour rates undercount older videos and linear extrapolation overcounts young ones.
- Don't mix in a day after a mass upload: on the observed channel the next day's uploads all got low views (account throttling is a hypothesis, the low counts are not).
- Don't mix platforms: [no cross-platform transfer](analytics-no-cross-platform-transfer.md).

## Evidence
One small channel, snapshot 28 Oct 2026 (public view counts, no login):
- Raw medians said one 3D style was dead: YouTube 9 / TikTok 4 against 1,148 / 896 for another style. But 8 of its 11 YouTube videos and 17 of its 22 TikTok videos had gone out in slots 4+ or on the day after a 22-upload day.
- In slots 1–3 (YouTube) / 1–5 (TikTok) on the same day the "dead" style scored YouTube 1,067 against 972 and 1,146 for two other styles (TikTok 285 against 266 and 268). On another day: 501 and 219 against 518.
- With n=3 per side in those slots the honest verdict was "no difference shown", not "the style doesn't work".

## Related
- [Spread uploads: only the first ~3 a day got views on one channel](../publishing/publishing-first-three-slots.md)
- [Views via yt-dlp](analytics-yt-dlp-views.md)
- [Platforms don't transfer](analytics-no-cross-platform-transfer.md)
