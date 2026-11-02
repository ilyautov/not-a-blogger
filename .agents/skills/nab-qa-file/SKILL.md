---
name: nab-qa-file
description: Use when checking a finished video's file identity, encoding, decode, dimensions, duration or loudness in not-a-blogger; not for judging frames or spoken wording.
---

# Technical checks on the final file

Read [AGENTS.md](../../../AGENTS.md) in the not-a-blogger checkout. Input: exact encoded MP4, expected format
and existing report. Identify the file by SHA256 and reject a stale report as evidence for another version.

Use [structural checks](../../../recipes/qa/qa-preflight-ffmpeg.md), the chosen build's finish procedure and
the existing [QA tools](../../../tools/README.md). Read [thresholds](../../../docs/QA-THRESHOLDS.md), preserving
their origin and scope. Inspect format/streams, dimensions, frame rate, duration, full decode, and final-audio
loudness/peak when audio exists. Source composition validity or a pre-encode master is not the encoded-file result.

Do not invent one generic tool command or adjust a threshold to get green. Missing tools/inputs remain unmeasured.
Report-only requests assess the supplied report without claiming a new measurement.

Output: file/hash, actual checks/values, failures and omissions. Preserve `preview_partial`, false technical status
and null speech checks; this subset alone is not overall completion. Route pixel inspection to picture QA and spoken
text/alignment to speech QA. Do not rewrite scenes, synthesize audio, rerender or publish while checking file properties.
