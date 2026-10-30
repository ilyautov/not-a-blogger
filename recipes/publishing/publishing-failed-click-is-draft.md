---
id: publishing-failed-click-is-draft
title: Find a stuck Short as a draft in the Shorts tab instead of re-uploading
section: publishing
lang: any
status: hypothesis
evidence: experience
tools: [YouTube Studio]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-23
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
"Publish" did nothing and it seems nothing was uploaded. Studio keeps the button inactive while it shows "Processing will begin shortly": the click goes nowhere, but the file already sits as a draft. Re-uploading creates a duplicate. Second trap: vertical videos live in the "Shorts" tab, not "Videos"; searching Videos by a similar title opens an already published long video instead.

## Do
1. Studio → Content → "Shorts" tab for vertical, "Videos" for horizontal. A vertical video **longer than 180 s** is not a Short: YouTube files it as a regular video, so look for it in "Videos".
2. Filter by visibility "Draft", not by title prefix.
3. Open the draft, wait for processing to finish, walk the wizard to "Publish".
4. "Video processing is taking longer than usual" during upload also means the draft already exists. Don't wait for the checks to finish and don't re-upload: read the draft's row in Studio, finish the wizard, then record the video id.
5. If your automation drives a browser profile and the browser was killed (timeout), the profile may keep a `SingletonLock` pointing at a dead process, and every next run reports "profile busy". Remove the lock only after checking that the process is gone:

```bash
pid=$(readlink "$PROFILE/SingletonLock" | sed 's/.*-//')
ps -p "$pid" >/dev/null || rm "$PROFILE/SingletonLock"
```

## Verify
One copy of the video in the right tab, visibility "Public", no drafts with the same file.

## Don't
- Don't re-upload before checking drafts.
- Don't expect a draft if the upload broke before 100 %: see [wait for 100 %](publishing-wait-upload-100.md).

## Evidence
- Written after a stuck draft was nearly confused with a published long video sharing its title prefix.
- "Processing is taking longer than usual": two uploads in one day; both were drafts already and were finished without re-uploading.
- A 197 s vertical video was published as a regular video and was found only in the "Videos" tab.
- A killed browser left a lock on a dead process once; the next runs waited on it until it was removed.
Experience, no case counts beyond these: hypothesis.

## Related
- [Wait for "Uploaded 100 %"](publishing-wait-upload-100.md)
