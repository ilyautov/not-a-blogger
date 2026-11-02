---
name: nab-publisher-builder
description: Use when building or specifying a personal video publisher with queues and browser adapters from not-a-blogger; not for sending an existing upload or logging into accounts.
---

# Build a separate publisher

Locate the not-a-blogger checkout and read its [publication contract](../../../AGENTS.md),
[publisher recipe](../../../recipes/publishing/publishing-build-your-publisher.md) and
[build brief](../../../docs/publisher/README.md) ([Russian](../../../docs/publisher/README.ru.md)).
No upload client or publisher CLI is shipped in this kit. Build in the person's chosen separate project; do not
pretend commands from the proposed interface already exist. Use an existing suitable stack, otherwise Node/TypeScript
with Playwright. Start with the requested first platform/account, not a claim of support for every platform.

Preserve these implementation contracts:

- Durable state per file hash/platform/account, metadata digest and intended visibility. Approval binds those exact
  values; reject a changed file or metadata before a side effect. A path or a general "looks good" is not that identity.
- Offline planning/dry-run is read-only and opens no browser. Atomic queue writes, exclusive job/profile ownership
  and stale-worker protection are part of recovery, not just success-path behavior.
- A crash or timeout after submit, or `uploading` found after restart, means `needs_review`. Inspect existing
  drafts/posts before retrying; missing saved ID does not prove failure. Preserve completed targets independently.
- Manual login in a dedicated profile; keep the login/upload browser channel consistent. Do not copy sessions,
  request passwords, use the everyday browser profile or commit authentication state.

Build the queue/fake adapter and the brief's offline acceptance cases first. Add real adapters individually, inspect
current official platform/Playwright documentation, and document each adapter's limits. Keep unavailable adapters
unavailable. A mock pass is not evidence of a live upload; an upload click or moderation is not verified publication.

Deliver code or, when only a specification was requested, the implementation brief: actual project paths, commands
that exist, test results, uncertain-outcome handling and commands for the person's controlled account test. Label
proposed commands as proposed. The person performs login and real sending separately. This skill never accesses
accounts, uploads or publishes as part of development and does not override the toolkit's publication rules.
