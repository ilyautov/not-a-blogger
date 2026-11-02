---
id: publishing-build-your-publisher
title: Build a separate publisher with a persistent queue and uncertain-outcome recovery
section: publishing
lang: any
status: hypothesis
evidence: experience
tools: [Playwright, Node.js, TypeScript]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-11-02
updated: 2026-11-02
contributors: [not-a-blogger]
---

## When
You want your agent to build a personal publisher for YouTube, TikTok or Instagram, instead of assembling
ad hoc upload scripts for every video. The toolkit currently supplies preparation/checking tools, not an uploader.

## Do
1. Read the [build brief](../../docs/publisher/README.md) ([Russian](../../docs/publisher/README.ru.md)). Choose one
   platform and one account for the first adapter; add the others after the first passes its acceptance checks.
2. Build in a separate project. Keep rendering independent: a finished file, its hash, metadata, target account
   and intended visibility enter a persistent queue. Persist state per platform/account/file, not one global `done`.
3. Implement offline planning first. A dry run validates inputs and prints the proposed work without opening a
   browser, contacting a platform or changing queue state. Approval identifies the exact file, metadata and target.
4. Use dedicated browser profiles with manual login. Keep profiles and authenticated state outside tracked files;
   use the same browser/channel for login and upload, one process per profile. Do not ask for passwords in chat.
5. Treat an upload click and a publication as different events. Save a returned platform ID immediately. If a click
   times out or a worker dies, move the attempt to `needs_review`: reconcile the existing draft/post before any retry.
6. Give the person the offline test results, adapter limitations and commands for their own controlled account test.
   Building the publisher does not authorize uploading a video; this toolkit's agent still hands publication to the person.

Copy the implementation task from the build brief. It specifies a CLI to implement; those commands are not shipped
in this repository. The existing `tools/publish-prep/credits.py` prepares attribution, not uploads.

## Verify
- Offline tests cover a changed file/metadata after approval, two workers, a crash after submit, malformed queue,
  an existing draft, a completed platform plus an unfinished platform, and a rejected or expired login.
- Planning performs no network/browser work and leaves the queue unchanged. Restarting never blindly replays an
  `uploading` job; a confirmed published record is skipped.
- The handoff distinguishes `offline_pass`, an account test the person actually performed, and platforms not tested.
  `published` requires the right account, platform ID/URL, intended visibility and saved verification evidence.

## Don't
- Don't copy the author's private publisher, profiles, queues or channel identifiers into the new project.
- Don't retry a timed-out submit automatically, overwrite an existing post, or mark all platforms done together.
- Don't ship guessed selectors as tested adapters, claim mock tests prove a live upload, or bypass login challenges.

## Evidence
The author's workshop uses a separate browser publisher with persistent profiles, queue records and post-upload
checks. Its operational failures motivated this design. This public build recipe has not been validated by building
and using a new publisher on real accounts: `hypothesis`. No upload client or credentials are included here.

## Related
- [Build brief and acceptance checks](../../docs/publisher/README.md)
- [Wait for upload completion](publishing-wait-upload-100.md)
- [Find the existing draft](publishing-failed-click-is-draft.md)
- [Check the audience flag](publishing-youtube-kids-flag.md)
