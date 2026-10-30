---
id: publishing-first-three-slots
title: Spread uploads over days, strongest first: on one small channel only the first ~3 YouTube and ~5 TikTok uploads of a day got views
section: publishing
lang: any
status: hypothesis
evidence: video-metric
tools: [YouTube Studio, TikTok Studio, yt-dlp]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-28
updated: 2026-10-29
contributors: [not-a-blogger]
---

## When
A batch day: several finished shorts, a backlog of remakes or a series. Everything uploads fine, but most of the batch gets single-digit views, and the next day you conclude "this style doesn't work".

## Do
1. Count uploads per platform per day. YouTube counts the day in **Pacific time**; for TikTok use UTC.
2. YouTube: plan **at most 3 uploads a day** as a precaution. Observed on one channel: videos from the 4th upload of the day on were accepted and published but got single-digit view counts. Why is not known: a per-account slot limit is a hypothesis, nobody measured impressions or got a platform statement.
3. TikTok: plan **at most 5** a day (on the observed channel the views dropped after the 5th–6th upload). On the day after a 22-upload day all ten new uploads got 1–75 views; account-level throttling is one possible explanation, not a confirmed one.
4. Put the strongest video first. Spread the rest over the next days via the queue file from [upload cap](publishing-youtube-daily-upload-cap.md).
5. Write the slot number next to every published video (`slot 2/3`, platform, date). Any later comparison of styles or topics needs it, see [compare in equal slots](../analytics/analytics-compare-in-equal-slots.md).

```python
from datetime import datetime
from zoneinfo import ZoneInfo
def yt_day(ts_utc: datetime) -> str:          # the day YouTube counts the slot in
    return ts_utc.astimezone(ZoneInfo("America/Los_Angeles")).date().isoformat()
```

## Verify
- The queue file has no day with more than 3 YouTube or 5 TikTok entries.
- 48 h after publishing, views of slots 1–3 are of the same order as your usual; if a slot-1 video is at single digits too, the cause is not the slot (check the kids flag, a twin upload, a shadow restriction).

## Don't
- Don't read "low views" as "bad style" for a video that went out in slot 4+ or on the day after a mass upload: on the observed channel those positions had low views whatever the style, so the comparison tells you nothing about the style.
- Don't re-upload videos that died in late slots without the person's decision: a re-upload may be caught as a duplicate (a twin got 108 views against 2,771 for the first version, see [no twin versions](publishing-no-twin-versions.md)).
- Don't take these numbers as platform rules or the slot mechanism as established: they are view counts of one small channel over two weeks, not impressions, and the cause is a hypothesis. Re-measure on yours, and don't use slot position as a universal filter for other people's data.

## Evidence
One small channel (Russian-language AI shorts), public view counts read without login 28 Oct 2026, ages 16–165 h:
- YouTube, slots 1–3 of the day: median ~970 views (n=17, range 501–2,771; the one miss, 108, was a twin of an earlier video). Slots 4 and later: median 9 (n=15, max 70), in every style.
- The same on another day two weeks earlier: the first two uploads 242 and 466, the next five 10–74.
- TikTok, a day with 22 uploads: the first six got 229–754 views, from the 7th on 0–60. The next day ten more uploads got 1–75 each (median 2–3), whatever their position.
- Two weeks of data, one channel; the TikTok threshold of 5–6 rests on two days. These are public view counts only: impressions, reach and any account restriction were not measured, so the slot quota and the throttling explanation are hypotheses. Status hypothesis for that reason.

## Related
- [Treat about 10 YouTube uploads a day as a hard block](publishing-youtube-daily-upload-cap.md)
- [Compare styles only in equal slots](../analytics/analytics-compare-in-equal-slots.md)
- [Views via yt-dlp](../analytics/analytics-yt-dlp-views.md)
