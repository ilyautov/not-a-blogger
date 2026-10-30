---
id: publishing-long-before-shorts
title: Publish Shorts only after the long video they link to is actually live
section: publishing
lang: any
status: hypothesis
evidence: experience
tools: [YouTube Studio, TikTok Studio, yt-dlp]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-23
updated: 2026-10-29
contributors: [not-a-blogger]
---

## When
Shorts cut from a long video must link to it. Uploaded before the long video is public (or before a stuck long video is re-uploaded), their descriptions carry an empty or dead link and must be rewritten one by one on every platform.

## Do
1. Upload the long video, wait for "Public", open its link in a logged-out window.
2. Check the link is live:

```bash
yt-dlp --skip-download --print "%(availability)s %(title)s" "https://youtu.be/<LONG_ID>"
```

3. Only then write Shorts descriptions: first line = link to the long video, then permanent links (channel, site), music and photo attribution if the license requires it.
4. Record the long video and every Short in the published registry.

## Verify
The link in every Short's description opens the public long video.

## Don't
- Don't rely on clickable description links in TikTok: not every account has them; point to the profile or a lead-magnet page.

## Evidence
No own count; descriptions of already published Shorts once had to be rewritten after the long video got stuck and was re-uploaded with a new link.

## Related
- [Wait for "Uploaded 100 %"](publishing-wait-upload-100.md)
- [YouTube Shorts: profile link or Related Video instead of a codeword](../cta/cta-youtube-link-in-description.md)
- Example: [A hook that blocks a dangerous command](../../examples/hook-vertical-from-long/README.md)
