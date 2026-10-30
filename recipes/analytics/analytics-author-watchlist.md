---
id: analytics-author-watchlist
title: Keep a tiered watchlist of niche authors and scan it once a day for reels above baseline
section: analytics
lang: any
status: hypothesis
evidence: experience
tools: [curl, python]
learn: ../../learn/en/01-idea-hook-script.md
added: 2026-10-27
updated: 2026-10-27
contributors: [not-a-blogger]
---

> **Terms of service and risk.** Automated collection may violate Instagram's Terms of Use, even read-only, without
> a login and with an honest user agent. Read only public pages, keep the rate low, and use this at your own risk.
> The author of this recipe has had his own Instagram account temporarily blocked.

## When
Ideas come from your head or from news, and by the time a niche hit is noticed it is two weeks old. You want fresh hits of your niche on the day they take off, from a known set of authors.

## Do
1. Keep a hand-curated TSV `watchlist.tsv`: `handle  tier  note`. Tiers: **A** = closest reference (every hit becomes a remake candidate), **B** = watch (check daily, pick selectively), **C** = occasionally (scan weekly or on demand). Edit tiers by hand after each review; the scan never changes them.
2. Once a day scan A+B: for each author take the reels of the last 3 days via the [embed method](analytics-instagram-embed-read-only.md), sequentially, ~30 s per author.
3. Baseline per author = median views of the last 12 reels older than 2 days (younger reels are still climbing and would drag the median).
4. A fresh reel with views ≥ 3× the author's baseline → write it to `candidates-<date>.tsv` with the ratio, the hook line and the post type.
5. Review candidates by hand the same day; the best one goes to a [remake](../idea/idea-remake-rhythm-not-words.md).

```python
import statistics, datetime as dt
def candidates(reels, today, k=3.0):
    # reels: [{"code", "views", "date"}] for one author, newest first
    old = [r["views"] for r in reels if (today - r["date"]).days > 2][:12]
    if len(old) < 5:
        return []                       # not enough history: no baseline, no verdict
    base = statistics.median(old)
    fresh = [r for r in reels if (today - r["date"]).days <= 3]
    return [(r, r["views"] / base) for r in fresh if r["views"] >= k * base]
```

## Verify
- The scan log has one line per A/B author per day with `ok` or `no data`; authors with `no data` three days in a row are flagged for a manual check, not retried harder.
- Every candidate row carries the baseline number it was compared to.
- Spot-check one candidate a week logged out: the ratio holds against what the post page shows.

## Don't
- Don't compare authors with each other: a 3× jump on a 2k baseline is a candidate, 50k flat on a 60k channel is not.
- Don't let the scan edit tiers or delete authors; that stays a hand decision.
- Don't include your own account in the scan as a "competitor"; use your own analytics for that.
- Don't store other people's media; store counters and codes.

## Evidence
Setup used on one watchlist of about a hundred authors in three tiers; daily scan of A+B fits in under an hour at ~30 s per author. The ×3 threshold and the 12-reel window are working values, not tuned on a sample: no measured precision of "candidate → actual hit" yet. The ×5 rule for hit *discovery* across a wide set is measured in [hits by median](../idea/idea-find-hits-by-median.md); this recipe is the daily follow-up on a narrow set, hence the lower threshold.

## Related
- [Read Instagram counters via embed](analytics-instagram-embed-read-only.md)
- [Hits by author median](../idea/idea-find-hits-by-median.md)
- [Remake a fresh proven hit](../idea/idea-remake-rhythm-not-words.md)
