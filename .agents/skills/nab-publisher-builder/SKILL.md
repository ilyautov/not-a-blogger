---
name: nab-publisher-builder
description: Use when coordinating a complete personal publisher implementation or selecting its next module from not-a-blogger; use focused publisher skills for individual components, never live account operation.
---

# Coordinate a separate publisher build

Locate the not-a-blogger checkout and read [AGENTS.md](../../../AGENTS.md), the
[publisher recipe](../../../recipes/publishing/publishing-build-your-publisher.md) and
[build brief](../../../docs/publisher/README.md) ([Russian](../../../docs/publisher/README.ru.md)).
No publisher CLI or upload client is shipped here. Build in the person's separate project, using its existing
suitable stack or Node/TypeScript with Playwright. Proposed commands remain proposed until implemented.

Select one component; do not load or implement everything for a narrow request:

| Module | Skill |
|---|---|
| Offline plan, durable queue, approval and ownership | [nab-publisher-queue](../nab-publisher-queue/SKILL.md) |
| One platform's preflight/upload/inspect/verify | [nab-publisher-adapter](../nab-publisher-adapter/SKILL.md) |
| Uncertain outcome, reconciliation and recovery | [nab-publisher-recovery](../nab-publisher-recovery/SKILL.md) |

For a complete build, establish the shared queue/state contract and fake-service tests first; add requested adapters
one at a time. Approval binds file SHA256, metadata, platform, account and visibility. A crash/timeout after submit
is uncertain and must be reconciled before retry, not blindly replayed. Completed targets remain independent.

Deliver code or the requested specification, actual commands/tests and untested integrations. The person performs
manual login and a separate controlled account test. Mock passes do not prove live uploads. This build skill never
accesses accounts, copies sessions, uploads or publishes and does not override the toolkit's publication policy.
