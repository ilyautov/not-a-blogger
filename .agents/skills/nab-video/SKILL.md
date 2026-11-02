---
name: nab-video
description: Use when making or revising a short video in the not-a-blogger toolkit, from a first silent demo to a voiced reel with a review handoff.
---

# Make a video with not-a-blogger

Work in a not-a-blogger checkout. Read its [AGENTS.md](../../../AGENTS.md) and the existing brief first. Paths below
are relative to that checkout, not to a global skill installation. If the checkout is unavailable, request its location.

Choose the build from the person's actual setup:

- Node 22+ and ffmpeg, first look at the engine: [starter-lite](../../../starter-lite/README.md), a silent 15-second
  demo. It has no voice or finished-file QA. Describe that output before starting; don't promise a voiced custom reel.
- Python/Node and a voiced build: [full starter](../../../starter/README.en.md). Use its existing
  [reel-starter skill](../../../starter/.agents/skills/reel-starter/SKILL.md), first task and local instructions.
- A specified format: choose a [template](../../../templates/README.md); read its README before changing it.

For a new script, use the person's topic, language and intended payoff. A supplied script that is already approved
does not need a second approval. Otherwise show the exact lines, visible action per line and first/last frame before
synthesis or render. For staging, use the bundled [direction map](../../../starter/.agents/skills/reels-direction/SKILL.md);
for camera, load [camera moves](../../../starter/.agents/skills/camera-moves/SKILL.md) only when needed. The
[style atlas](../../../learn/en/04-image-and-frame.md) is a source of treatments, not eight ready animation engines.

Find techniques in [recipes by symptom](../../../recipes/BY-SYMPTOM.md). Preserve topic-specific action rather than
renaming the demo's headlines. Read voice/language rules before synthesis; use the person's own or permitted voice.

After assembly follow the chosen build's checks and [delivery contract](../../../starter/DELIVERY.md). Hand over the
exact file/hash, contact sheet, measured results and omitted checks. A silent or fake/no-ASR render remains a partial
demonstration. Never infer listening, continuous viewing, artistic acceptance or publication from automated checks.
Prepare metadata for the person; do not upload or publish.
