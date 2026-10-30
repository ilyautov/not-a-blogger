---
id: analytics-yt-dlp-views
title: Pull public views of all your videos with one yt-dlp command and compare with the niche median
section: analytics
lang: any
status: proven
evidence: measurement
tools: [yt-dlp]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Views are checked one by one in Studio, by eye, after each video. A month later there is no table showing which formats pull and which are dead, nor whether your numbers are bad or normal for the niche.

## Do
1. Keep a file with links or IDs of all published videos (the published registry).
2. Take a snapshot with one command, date in the file name.
3. Compare with the median of similar channels, not with others' hits.

```bash
yt-dlp --skip-download --ignore-errors \
  --print "%(id)s	%(view_count)s	%(like_count)s	%(comment_count)s	%(upload_date)s	%(title)s" \
  -a ids.txt > views-$(date +%F).tsv
sort -t$'\t' -k2,2nr views-$(date +%F).tsv | head
```

## Verify
TSV line count = video count in `ids.txt`; resolve `NA` rows by hand (video deleted or hidden).

## Don't
- Don't look for retention, CTR or traffic sources here: yt-dlp gives only public counters; use Studio. Instagram and TikTok give incomplete counters without login.

## Evidence
Snapshot of 39 videos of one channel: Shorts ceiling 1.0–1.3k views; best performers were the everyday "asked an AI for X, got absurdity" story and a meme character; narrow tutorials 2–400, cuts from long videos 1–17, long videos 12–625. Median Shorts views for similar Western channels in the niche: 1.4–2.4k, so a 1.3k ceiling is normal for a small channel.

## Related
- [Don't transfer one platform's conclusion](analytics-no-cross-platform-transfer.md)
