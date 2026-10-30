---
id: publishing-youtube-daily-upload-cap
title: Treat about 10 YouTube uploads a day as a hard block, not as a plan
section: publishing
lang: any
status: proven
evidence: measurement
tools: [YouTube Studio]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-27
updated: 2026-10-29
contributors: [not-a-blogger]
---

## When
A batch day: a long video plus Shorts, or a backlog of remakes. Around the eleventh upload of the day YouTube answers "upload unavailable, try again in 24 hours" and asks the channel to pass verification. No draft is created; the file is simply not accepted.

## Do
1. Plan by views, not by this cap: on one small channel only the first **3 YouTube uploads per Pacific-time day** got more than a handful of views, see [first three slots](publishing-first-three-slots.md) (the cause is a hypothesis). The ~10 here is the technical ceiling where uploads are refused; videos 4–10 went through but got single-digit to double-digit views.
2. If you still upload more (an archive dump, a test), stay at 9 or fewer, so one retry fits under the block. Keep the rest in a dated queue file: path, title, caption, platforms left. Next day starts from the queue, not from new builds.
3. Title = first line of the caption, cut at the last full sentence before 100 characters (YouTube's title limit). Keep the full caption as the description.
4. On TikTok paste the remainder of the caption into the description once; don't repeat the title line there.
5. If the block hits anyway: stop uploading to YouTube for the day, publish the queued items on the other platforms, and mark them in the queue.

```python
def yt_title(caption: str, limit: int = 100) -> str:
    first = caption.strip().splitlines()[0]
    if len(first) <= limit:
        return first
    cut = max(first.rfind(p, 0, limit) for p in ".!?")
    return first[:cut + 1] if cut > 0 else first[:limit].rsplit(" ", 1)[0]
```

## Verify
- Studio → Content shows exactly the uploads you counted for today, none stuck at "processing" and no row missing.
- The queue file for tomorrow lists every video that did not go out, with its platforms.
- No title in Studio is truncated with "..." (all under 100 characters).

## Don't
- Don't retry the blocked upload in a loop or from a second browser: it does not create a draft and does not shorten the 24 h.
- Don't split the day's batch across two channels to dodge the cap.
- Don't drop the kids-flag check because the day is long: it applies to every upload (see [kids flag](publishing-youtube-kids-flag.md)).

## Evidence
- 26 Oct 2026, one small channel: 10 uploads went through, the 11th returned "upload unavailable, try again in 24 hours, pass verification"; no draft appeared in Studio. The next day the same happened on the 11th upload again: exactly 10 per day on this channel. The number may depend on channel age and verification status.
- Passing the cap is not the same as being shown: in the same days uploads 4–10 got a median of 9 views against ~970 for uploads 1–3, see [first three slots](publishing-first-three-slots.md). An earlier version of this recipe said "plan 9 a day": on the day that plan was followed, 7 of 10 uploads landed in slots 4+ (8–27 views each).

## Related
- [Spread uploads: only the first ~3 a day got views on one channel](publishing-first-three-slots.md)
- [Check the "made for kids" flag after every upload](publishing-youtube-kids-flag.md)
- [Wait for "Uploaded 100 %"](publishing-wait-upload-100.md)
- [Failed click is a draft](publishing-failed-click-is-draft.md)
