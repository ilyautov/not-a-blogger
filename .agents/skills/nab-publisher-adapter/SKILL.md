---
name: nab-publisher-adapter
description: Use when implementing or specifying one platform's preflight, upload and inspect/verify adapter in a separate publisher based on not-a-blogger; not live account operation.
---

# One platform adapter

Read [AGENTS.md](../../../AGENTS.md) and the [adapter contract](../../../docs/publisher/README.md) in the
not-a-blogger checkout. Input: the separate publisher project, one requested platform/account alias and its existing
queue/approval/recovery interfaces. Reuse those contracts rather than building a second queue inside the adapter.

Consult current official platform and Playwright documentation when implementing the chosen interface. Implement
preflight, upload, inspect and verify; save an observed platform ID promptly. Distinguish a draft, transfer completion,
moderation and verified intended visibility. UI selectors are proposed until tested in the documented environment.

Use a dedicated profile, consistent login/upload browser channel and exclusive profile ownership. Login/MFA are
performed by the person. Never copy sessions or require credentials in chat. Make expired login, changed UI and
uncertain submit explicit outcomes; pass uncertainty to recovery instead of starting another upload.

Output: one adapter or its requested specification, fake/local-fixture tests, supported environment and known gaps,
plus instructions for the person's separate controlled account test. Keep other platforms unavailable until implemented.
Mock tests do not prove an account upload. Do not access live accounts, log in or submit a video during development;
do not change queue architecture or build every platform to finish a single-adapter request.
