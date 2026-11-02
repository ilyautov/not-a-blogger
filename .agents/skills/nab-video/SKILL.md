---
name: nab-video
description: Use when coordinating a complete short video or choosing its next production stage in not-a-blogger; use a focused skill for a single-stage request.
---

# Coordinate a video

Read [AGENTS.md](../../../AGENTS.md) and the existing brief in a not-a-blogger checkout. If the checkout is
unavailable, request its location. Preserve the person's scope, approved inputs and existing authorization.

For a first Node/ffmpeg-only demonstration choose [starter-lite](../../../starter-lite/README.md): 15 seconds,
silent, no finished-file QA. For voiced production use the [full starter](../../../starter/README.en.md) and its
local instructions. Choose a [template](../../../templates/README.md) when the requested format calls for it.

Load only the skill for the current task; the [directory](../../../.agents/skills/README.md) lists inputs and outputs:

| Task | Skill |
|---|---|
| Spoken script/hook | [nab-script](../nab-script/SKILL.md) |
| Visible action/framing | [nab-shot-plan](../nab-shot-plan/SKILL.md) |
| Still images/backgrounds | [nab-assets](../nab-assets/SKILL.md) |
| Animation/camera/cuts | [nab-motion](../nab-motion/SKILL.md) |
| Spoken takes | [nab-voice](../nab-voice/SKILL.md) |
| Music/SFX/mix | [nab-sound](../nab-sound/SKILL.md) |
| Subtitles/overlays | [nab-captions](../nab-captions/SKILL.md) |
| MP4 assembly | [nab-render](../nab-render/SKILL.md) |
| Whole-file review | [nab-video-qa](../nab-video-qa/SKILL.md) |
| Publication materials | [nab-publish-prep](../nab-publish-prep/SKILL.md) |

A narrow request does not restart this entire route. Reuse approved artifacts; changed spoken lines need approval
before production. Do not load every skill or require separate agents. A fake/no-ASR or silent demo retains its
partial scope. Deliver the exact file/hash and check limitations; the person reviews and publishes.
