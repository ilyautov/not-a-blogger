---
name: nab-video-qa
description: Use when reviewing a rendered MP4 or a video QA report in not-a-blogger, especially when deciding what green, missing or partial checks actually establish.
---

# Check the exact finished file

Use the not-a-blogger checkout and its [AGENTS.md](../../../AGENTS.md). Locate the exact MP4, approved script,
chosen build and current QA report. If only a report is supplied, assess that report; don't claim you measured or
watched an unavailable file. Do not rebuild or rewrite the video merely to review it.

First identify the MP4 by SHA256 and compare it with the report. A stale/missing hash does not establish checks on
this version. Read [QA-THRESHOLDS.md](../../../docs/QA-THRESHOLDS.md), then use the relevant existing tools from
[tools/README.md](../../../tools/README.md) and the build's documented finish command. Inspect tool help for inputs;
don't invent a generic QA CLI or silently install voice models to make a missing check disappear.

Use [final-file structural checks](../../../recipes/qa/qa-preflight-ffmpeg.md),
[frame fill](../../../recipes/qa/qa-frame-fill-mp4.md),
[voice checks](../../../recipes/qa/qa-voice-gate.md) and
[word sync](../../../recipes/qa/qa-word-sync-check.md) as applicable. Distinguish checks of rendered pixels/audio
from source/composition checks. Silent builds have no speech to validate; fake/no-ASR voice demos cannot establish
spoken-word accuracy. Preserve `preview_partial`, false technical status and null/unmeasured checks as reported.

Generate or locate a [contact sheet from the final MP4](../../../recipes/qa/qa-contact-sheet-final.md), inspect it
and open suspect frames. If the environment cannot inspect images, state that limitation. A sheet cannot establish
continuous motion, precise lip sync or how the audio sounds. Record listening/viewing only when actually performed.

Return a concise verdict, file/hash, checks run with results, missing checks, visual findings and remaining review
by the person. Use the [delivery passport](../../../starter/DELIVERY.md) for details. Keep machine status, readiness
for preview, artistic approval and permission to publish separate. Neither the skill nor a green report grants approval.
