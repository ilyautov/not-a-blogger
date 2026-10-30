---
id: analytics-telegram-reactions-36h
title: Measure Telegram posts by reactions per 1000 views, within 36 hours only
section: analytics
lang: any
status: proven
evidence: measurement
tools: [Telegram, spreadsheet]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
In Telegram reach is nearly equal across a channel's posts (subscribers see everything), so comparing genres by views shows nothing. Reactions come only in the first day to day and a half; afterwards views grow, reactions stall, and the ratio falls on its own.

## Do
1. Genre metric: reactions / views × 1000.
2. Compare posts of the same age, no older than 36 hours.
3. Don't add measurements older than the window to the series.

```text
post  age_h  reactions  per_1000
A     20.1   10         44.4
A     29.1   10         41.5     <- no new reactions, views grew, ratio fell
```

## Verify
For two measurements of one post inside 36 h, reactions grow with views; outside the window reactions stall.

## Don't
- Don't treat the genre ranking as law: it rests on five posts of one channel.
- Don't normalize ranked feeds (LinkedIn etc.) this way: there reach itself is a metric and differs severalfold.

## Evidence
- Five posts of different genres in a row: reach 33.3–35.8 views per hour, 7 % spread. Reactions per 1000 views: breakdown 33.3, question 24.0, counter-position 18.6, news reply 8.8, short reply 6.5. Breakdown 5.1× above short reply.
- One post: 44.4 reactions per 1000 at 20.1 h and 41.5 at 29.1 h with the same 10 reactions.
- Over 13.5 hours across 14 posts only the two freshest gained reactions; posts older than three days gained none while views grew.

## Related
- [Unique external commenters](analytics-unique-external-authors.md)
- [Don't transfer one platform's conclusion](analytics-no-cross-platform-transfer.md)
