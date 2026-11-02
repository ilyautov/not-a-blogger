---
name: nab-publisher-queue
description: Use when implementing or specifying the offline queue, approval identity and worker ownership of a personal publisher based on not-a-blogger; not platform UI adapters.
---

# Publisher queue and approval store

Read [AGENTS.md](../../../AGENTS.md) and the [publisher brief](../../../docs/publisher/README.md) in a
not-a-blogger checkout. Input: the person's separate publisher project, job schema and requested queue changes.
This toolkit supplies a design, not an existing queue API. Label proposed interfaces honestly.

Implement only persistent planning/state and its fake-service tests. Key targets by file hash/platform/account;
store metadata digest, intended visibility, attempt history and returned platform IDs. Approval binds exact inputs;
reject a changed file, caption, account or visibility before side effects. Completed platforms remain independent.

Use atomic persistence, exclusive job/profile ownership and stale-worker protection. Dry-run must leave the queue
unchanged and do no network/browser work. On restart, an `uploading` attempt becomes uncertain (`needs_review`),
not automatically ready for replay. Integrate with recovery through an explicit state contract; don't invent a claim
of exactly-once delivery from a local lock.

Output: queue/schema code or the requested specification, actual command/help information where implemented,
and offline tests for stale approval, competing workers, interrupted writes and partial target completion. No browser
adapter, manual login or live send is needed to complete this task. Keep unimplemented integrations unavailable.
