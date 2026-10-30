---
id: idea-format-lifecycle-week
title: Treat a borrowed format as perishable, take it within days and keep only the structure
section: idea
lang: any
status: hypothesis
evidence: video-metric
tools: [yt-dlp]
learn: ../../learn/en/01-idea-hook-script.md
added: 2026-10-28
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
You picked someone else's hit as a reference and plan to make your version "next week", or you want to copy its exact storyline.

## Do
1. Before building, get the reference's publish date and the dates of visible copies of the same formula.
2. Reference younger than about 3 days and no copies yet: the format is fresh, build it now.
3. Copies already out: take the structure (beats, rhythm, framing), put your own situation inside. Never reuse the storyline: it is taken after the second copycat.
4. Don't plan sequels of a hit on the same storyline, yours or someone else's.
5. Note the reference date and the number of copies next to the idea, so the choice can be checked later.

```bash
yt-dlp --skip-download --print "%(upload_date)s %(view_count)s %(title)s" "<reference-url>"
```

## Verify
The idea card has the reference's upload date, the build date and a copy count. If the gap is more than a few days and copies exist, the script's storyline differs from the reference in one sentence ("same beats, different situation").

## Don't
- Don't read this as "copying is dead": copying a reference's structure is still the default way to pick ideas.
- Don't treat the numbers below as a law: they come from public counters, not an experiment.

## Evidence
From our snapshots of AI-niche reels and shorts (September–October 2026, public rounded counters, no completion data): a formula gives ×200+ of the creator's median in the first 3 days, then copies arrive and the multiple drops 10–40×; a specific storyline is taken after the second copycat; sequels of a hit on the same storyline don't repeat its success. One format in the sample ("the agent was shown an ordinary thing → something impossible") faded within 3–4 days. Source: `research/findings.en.md` point 9, `research/formats.en.md` point 3. Correlation, so `hypothesis`.

## Related
- [Take ideas from niche hits selected by the author's median](idea-find-hits-by-median.md)
- [Remake rhythm, not words](idea-remake-rhythm-not-words.md)
- [Don't repeat your own hit](idea-no-repeat-own-hit.md)
- Research: [findings](../../research/findings.en.md), [formats](../../research/formats.en.md)
