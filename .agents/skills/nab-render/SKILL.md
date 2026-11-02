---
name: nab-render
description: Use when assembling or rerendering an MP4 from existing approved script, scenes, assets and audio in not-a-blogger; not for inventing a new script or visual concept.
---

# Assemble the approved inputs

Use the not-a-blogger checkout and [AGENTS.md](../../../AGENTS.md). Identify the chosen starter/template and read
its README/local instructions. Input: approved script and current scene/audio assets, build configuration and requested
output. Missing production inputs are a gap; do not fill them with a new concept or a silently changed voice.

Run the documented build for that project. Keep its incremental state, time contract, frame size/rate and lock
behavior; serialize heavy work per [assembly guidance](../../../recipes/assembly/assembly-serialize-heavy-jobs.md).
Rebuild the requested changed stage where supported. The [silent starter](../../../starter-lite/README.md) has no
finished-file QA; the [full starter](../../../starter/README.en.md) has a documented fake/no-ASR route and a separate
real-voice path. Do not call either demonstration fully verified speech.

Output: actual MP4 path, SHA256, duration/format and build/check reports, preserving partial status and failures.
Pass the file to [file QA](../nab-qa-file/SKILL.md), with picture/speech checks when requested or required by the
build's handoff. Use [DELIVERY.md](../../../starter/DELIVERY.md) for the complete delivery contract. Do not infer
artistic acceptance from exit zero, or publish the file. A dry run or failed build is not an MP4 delivery.
