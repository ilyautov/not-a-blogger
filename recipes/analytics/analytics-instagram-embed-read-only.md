---
id: analytics-instagram-embed-read-only
title: Read public Instagram counters through the embed page with an honest user agent
section: analytics
lang: any
status: hypothesis
evidence: experience
tools: [curl, python]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-27
updated: 2026-10-27
contributors: [not-a-blogger]
---

> **Terms of service and risk.** Automated collection may violate Instagram's Terms of Use, even read-only, without
> a login and with an honest user agent. Read only public pages, keep the rate low, and use this at your own risk.
> The author of this recipe has had his own Instagram account temporarily blocked.

## When
You need view and like counts of other authors' reels for a watchlist or a hit scan, without logging in, without an API key and without pretending to be a browser or a crawler.

## Do
1. Fetch only the public embed page: `https://www.instagram.com/reel/<code>/embed/captioned/` for a reel, `https://www.instagram.com/p/<code>/embed/captioned/` for a photo or carousel.
2. Send the real client name as the user agent (`curl/8.x` is what curl sends by default). No cookies, no session, no login.
3. Parse the counters out of the returned HTML; store the numbers with the date in a TSV, not the HTML.
4. If the embed is closed (private account, removed post, login wall, empty counters): record `no data` and move on. There is no step 5.

```bash
code=ABC123xyz
curl -sL -A "curl/8.7.1" "https://www.instagram.com/reel/$code/embed/captioned/" -o embed.html
grep -oE '"(video_view_count|edge_media_preview_like|edge_liked_by)":\{?"?count"?:?[0-9]+' embed.html || echo "no data"
```

## Verify
- A known public reel returns a view count that matches what you see on the post page logged out.
- A photo post via `/reel/<code>/embed/` returns "Unavailable" without counters; the same code via `/p/<code>/embed/` returns them. A reel via `/p/` returns likes but no view count: choose the path by post type.
- Throughput: about 30 s per author for the last few posts, sequential, no parallel fetching.

## Don't
- Don't impersonate a crawler or a browser (`Googlebot`, `Mozilla/5.0 ...`): the data you get is the data the owner chose to show the public, not what a spoofed client is served.
- Don't log in with a publisher account to read other people's numbers: that mixes reading and publishing on one profile and risks that profile.
- Don't store other people's media (frames, video, audio) outside a local evidence folder; keep the counters, not the content.
- Don't retry a closed embed with another path, header or proxy: the answer is `no data`.

## Evidence
Observations from one scanning setup, no controlled measurement: ~30 s per author per scan; the `/reel/` embed of a photo post comes back "Unavailable" without counters while `/p/` returns them; `/p/` for a reel gives no view count. Counters are rounded by the platform and have no retention data. Instagram can change the embed markup at any time; re-check the parser when a whole run returns `no data`.

## Related
- [Author watchlist scanned daily](analytics-author-watchlist.md)
- [Hits by author median](../idea/idea-find-hits-by-median.md)
- [Pull views with one yt-dlp command](analytics-yt-dlp-views.md)
