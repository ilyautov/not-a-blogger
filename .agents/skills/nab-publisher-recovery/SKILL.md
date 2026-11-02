---
name: nab-publisher-recovery
description: Use when analyzing an uncertain video submission from queue/log evidence or implementing publisher reconciliation after a crash/timeout in not-a-blogger; not a fresh upload request.
---

# Reconcile an uncertain attempt

Use [AGENTS.md](../../../AGENTS.md) and the [publisher recovery contract](../../../docs/publisher/README.md)
from the not-a-blogger checkout. Input: supplied queue/attempt history, file/account/platform identity and any recorded
IDs or platform evidence; for code work, the separate publisher project. No reconcile CLI is shipped in this toolkit.

An `uploading` attempt found after a crash, or a timeout after submit, means `needs_review`. Missing ID is not proof
of failure. Preserve all evidence and completed targets; do not reset the job to `ready` or infer a safe retry from a
local timeout. A known draft is reusable; moderation/processing is not verified publication.

For an incident review, produce the evidence assessment and exact inspection steps for the person to find an existing
draft/post. With insufficient evidence, stop at uncertainty. Do not access accounts or send a second upload to discover
what happened. For implementation, build reconciliation against the existing queue/adapter contracts and fake-service
tests: crash after successful submit, lost ID, found draft, ambiguous match and a finished platform beside an unfinished one.

Output: incident findings with confirmed/unknown state, or the requested recovery code/specification and offline test
results. Cite actual artifact paths/IDs without pretending proposed commands already exist. No blind replay, live login,
metadata overwrite, new adapter or new submission as part of recovery analysis/development.
