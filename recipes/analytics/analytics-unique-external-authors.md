---
id: analytics-unique-external-authors
title: Compare posts by unique external commenters per 1000 impressions, not the comment counter
section: analytics
lang: any
status: proven
evidence: measurement
tools: [spreadsheet]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The comment counter includes the author's own replies and repeat comments from the same people. A post where the author replied a lot looks "engaging" though it has as many outside voices as its neighbour.

## Do
1. Expand the whole thread and compute:

```text
external_authors = unique commenter names, excluding the post author
metric           = external_authors / impressions * 1000
inflation        = (all_comments / impressions * 1000) / metric
```

2. Log the metric in the posts table, not the platform counter.

## Verify
For two posts with similar counters compute the author-reply share: if it differs a lot, the counter comparison was false.

## Don't
- Don't overtrust the metric where threads can't be fully expanded: it's computed on the visible part and undercounts.

## Evidence
Post with 17,581 impressions: platform counter 24, 23 entries expanded, 10 of them author replies (43.5 %), 11 external authors. By counter 1.37 comments per 1000 impressions, by unique external 0.63: 2.2× inflation. On a question post by the same author inflation reached 5.5×.

## Related
- [Telegram reactions in a 36 h window](analytics-telegram-reactions-36h.md)
- [Codeword in comments](../cta/cta-codeword-in-comments.md)
