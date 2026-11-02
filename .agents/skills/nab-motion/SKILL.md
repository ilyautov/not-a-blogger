---
name: nab-motion
description: Use when designing or implementing camera movement, object animation, cuts or transitions for existing short-video scenes in not-a-blogger.
---

# Motion and camera

Use the not-a-blogger checkout and [AGENTS.md](../../../AGENTS.md). Input: shot plan, existing scene code,
assets, duration and word/event timings. Preserve approved speech and unrelated scenes.

Choose motion for the event using [camera moves](../../../starter/.agents/skills/camera-moves/SKILL.md),
[camera recipes](../../../recipes/camera/README.md) and
[transitions](../../../recipes/transitions/README.md). Distinguish an object's action from camera movement:
a slow push-in cannot make a static scene act. Explain what each chosen move reveals or emphasizes.

Keep the existing renderer's time contract: [deterministic frames](../../../recipes/assembly/assembly-deterministic-timeline.md),
[word anchors](../../../recipes/assembly/assembly-word-anchored-animation.md) and
[tween lifetimes](../../../recipes/assembly/assembly-gsap-tween-lifetime.md). Use the project's current frame rate
and duration; don't globally change them to make a local move work. Inspect dry frames and run applicable motion/stillness
checks; camera-only movement must not be presented as verified object action.

Output: a scoped scene/timeline change or, for a planning request, move specifications with timings. Include inspected
frames and limits of the inspection. Do not regenerate images/voice, rebuild unrelated scenes or claim a final MP4
review from source frames. Hand off to render when a final file is requested.
