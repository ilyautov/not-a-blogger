---
id: analytics-no-cross-platform-transfer
title: Don't transfer a "format works" conclusion from one platform to another
section: analytics
lang: any
status: proven
evidence: video-metric
tools: [spreadsheet]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A video took off on one platform and the format is declared working everywhere. Or it flopped on YouTube and the topic is buried, though it might have hit on Instagram.

## Do
1. Keep a "video × platform" table, not a "video" table.
2. Draw format conclusions per platform.
3. Use a per-platform metric: views and impressions for ranked feeds, reactions per 1000 for Telegram.

```text
video        instagram   youtube   tiktok
tv-no-ads    212000      <=328     <=328
```

## Verify
Every format conclusion names its platform.

## Don't
- Don't transfer conclusions between periods either, if you have one platform: algorithms change.

## Evidence
One reel: 212k views and 7.5k likes on Instagram in the first evening, 21.5k likes and 257 comments a day later; 1 to 328 views on YouTube and TikTok. In Telegram five posts of different genres got the same reach (7 % spread), while on LinkedIn the same topics differed 2.5× in impressions.

## Related
- [Pull views with yt-dlp](analytics-yt-dlp-views.md)
- [Telegram reactions in a 36 h window](analytics-telegram-reactions-36h.md)
