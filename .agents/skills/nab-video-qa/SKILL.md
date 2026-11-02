---
name: nab-video-qa
description: Use when coordinating an overall finished-video review in not-a-blogger or deciding which QA checks are needed; use a focused QA skill for only one check domain.
---

# Coordinate final review

Use the not-a-blogger checkout and [AGENTS.md](../../../AGENTS.md). Identify the exact MP4/hash, approved script,
current report and requested review scope. If only a report is supplied, assess the report without claiming new
measurement, viewing or listening.

Load only the applicable procedure:

| Evidence needed | Skill |
|---|---|
| Identity, encoding, decode, dimensions, duration, final loudness | [nab-qa-file](../nab-qa-file/SKILL.md) |
| Rendered frames, contact sheet, clipping, visual fill | [nab-qa-picture](../nab-qa-picture/SKILL.md) |
| Recognized words, alignment, pauses, voice regressions | [nab-qa-speech](../nab-qa-speech/SKILL.md) |

For overall review, combine results for the same exact file and name gaps/conflicting report versions. For a
picture-only or speech-only request, keep the other checks outside the performed scope. Use the shared
[threshold table](../../../docs/QA-THRESHOLDS.md), not invented stricter/looser values.

Deliver verdict, file/hash, measured checks, findings and omissions per [DELIVERY.md](../../../starter/DELIVERY.md).
Preserve `preview_partial`, false technical status and null/unmeasured checks. A subset pass is not full completion;
contact sheets are not continuous viewing or listening. Keep technical status, readiness for preview, artistic
approval and publication permission separate. Do not repair, rerender or publish merely to perform review.
