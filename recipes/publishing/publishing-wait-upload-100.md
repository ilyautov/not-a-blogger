---
id: publishing-wait-upload-100
title: Keep the YouTube Studio tab open until a large file reaches 100 %
section: publishing
lang: any
status: hypothesis
evidence: experience
tools: [YouTube Studio]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-23
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
For a long video (over 100 MB) a processing dialog appears after file selection and it seems YouTube will finish on its own. Close the tab and the upload hangs; Studio may never offer "Resume upload".

## Do
1. Keep the tab open until the wizard footer shows "Uploaded 100 %".
2. Only then click "Publish" or "Save".
3. Compress very large files to a reasonable bitrate first to shorten the risk window.

```bash
ls -lh final.mp4
ffprobe -v error -show_entries format=duration,bit_rate -of default=nw=1 final.mp4
```

## Verify
No upload-error mark in Studio; the video plays to the end.

## Don't
- Don't upload over a weak connection: a network drop breaks the upload even with the tab open; use wired internet.

## Evidence
A long video over 100 MB hung at 49 % after the tab was closed right after the processing dialog; resuming failed, the stuck video was deleted and re-uploaded.
One incident. To promote: N uploads over 100 MB with the tab kept open until 100 %, zero stuck at processing; or a second documented hang after an early close.

## Related
- [Stuck draft in Shorts](publishing-failed-click-is-draft.md)
